import os
import json
import logging
import signal
import time
from datetime import datetime, timedelta, date

import paho.mqtt.client as mqtt
import psycopg2
import psycopg2.extras as pg_extras
import joblib
import numpy as np
from scipy.signal import welch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Global models and buffers
# -------------------------------------------------
_SVM_MODEL = None
_KNN_MODEL = None
_SAMPLE_BUFFER = []  # (dt, eeg1, eeg2, ecg)

# -------------------------------------------------
# Load models
# -------------------------------------------------
try:
    _SVM_MODEL = joblib.load("svm_fatigue_model.joblib")
    logger.info("Loaded SVM fatigue model")
except Exception as e:
    logger.warning("Could not load SVM model: %s", e)

try:
    _KNN_MODEL = joblib.load("knn_eeg_bandpower_model.joblib")
    logger.info("Loaded KNN action model")
except Exception as e:
    logger.warning("Could not load KNN model: %s", e)

# -------------------------------------------------
# EEG feature utilities (for KNN)
# -------------------------------------------------
BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 45),
}

ACTION_LABELS = {
    0: "brake",
    1: "turn",
    2: "change",
    3: "throttle",
    4: "stable",
}

def bandpower(signal, sf, band):
    low, high = band
    freqs, psd = welch(signal, sf, nperseg=sf * 2)
    idx = np.logical_and(freqs >= low, freqs <= high)
    return np.mean(psd[idx])

def extract_knn_features(ch1, ch2, sf=250):
    feats = []
    for sig in (ch1, ch2):
        for band in BANDS.values():
            feats.append(bandpower(sig, sf, band))
    return np.array(feats)[None, :]

# -------------------------------------------------
# MQTT callbacks
# -------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        topic = userdata.get("topic")
        qos = userdata.get("qos", 0)
        if topic:
            client.subscribe(topic, qos=qos)
            logger.info("Subscribed to %s (qos=%s)", topic, qos)
    else:
        logger.error("Failed to connect, rc=%s", rc)

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")

    try:
        s = payload
        parts = [p.strip() for p in s.split(",") if p.strip()]
        if len(parts) <= 1:
            return

        entries = parts[1:]
        timestamp = None
        if ";" in entries[-1]:
            last_data, ts = entries[-1].split(";", 1)
            entries[-1] = last_data.strip()
            timestamp = ts.strip()

        def to_num(x):
            try:
                return float(x)
            except Exception:
                return None

        records = []
        for e in entries:
            cols = [c.strip() for c in e.split("|")]
            if len(cols) < 3:
                continue
            records.append({
                "eeg1": to_num(cols[0]),
                "eeg2": to_num(cols[1]),
                "ecg": to_num(cols[2]),
            })

        if not records:
            return

        sfreq = float(os.getenv("EEG_SFREQ", "250"))
        n = len(records)

        if timestamp:
            try:
                t = datetime.strptime(timestamp, "%H:%M:%S").time()
                base_dt = datetime.combine(date.today(), t)
            except Exception:
                base_dt = datetime.utcnow()
        else:
            base_dt = datetime.utcnow()

        delta = 1.0 / sfreq
        sample_times = [
            base_dt - timedelta(seconds=(n - 1 - i) * delta)
            for i in range(n)
        ]

        rows = []
        for dt, r in zip(sample_times, records):
            if None in (r["eeg1"], r["eeg2"], r["ecg"]):
                continue
            rows.append((
                dt,
                int(round(r["eeg1"])),
                int(round(r["eeg2"])),
                int(round(r["ecg"])),
            ))

        for r in rows:
            _SAMPLE_BUFFER.append(r)

        state_prediction = None
        action_prediction = None

        if len(_SAMPLE_BUFFER) >= 150:
            try:
                last150 = _SAMPLE_BUFFER[-150:]
                ch1 = np.array([x[1] for x in last150], dtype=float)
                ch2 = np.array([x[2] for x in last150], dtype=float)

                # ---- Fatigue (SVM) ----
                if _SVM_MODEL is not None:
                    svm_feat = np.concatenate([ch1[:100], ch2[:100]])[None, :]
                    svm_pred = _SVM_MODEL.predict(svm_feat)
                    state_prediction = "normal" if svm_pred[0] == 0 else "fatigued"

                # ---- Action (KNN + PSD) ----
                if _KNN_MODEL is not None:
                    knn_feat = extract_knn_features(ch1, ch2)
                    knn_pred = int(_KNN_MODEL.predict(knn_feat)[0])
                    action_prediction = ACTION_LABELS.get(knn_pred, "unknown")

                logger.info(
                    "Predictions | state=%s | action=%s",
                    state_prediction,
                    action_prediction,
                )

            except Exception:
                logger.exception("Prediction failed")

        if not rows:
            return

        conn = None
        try:
            conn = psycopg2.connect("postgres://postgres:password@localhost:5432/eeg")
            conn.autocommit = False
            cur = conn.cursor()

            time_from = rows[0][0]
            time_to = rows[-1][0]
            user_id = int(os.getenv("DEFAULT_USER_ID", "1"))

            cur.execute(
                """
                INSERT INTO recordings
                (time_from, time_to, state_prediction, action_prediction, user_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (time_from, time_to, state_prediction, action_prediction, user_id),
            )
            recording_id = cur.fetchone()[0]

            rows_with_rec = [
                (r[0], r[1], r[2], r[3], recording_id)
                for r in rows
            ]

            insert_sql = """
                INSERT INTO samples
                (time_stamp, eeg1, eeg2, ecg, recording_id)
                VALUES %s
            """
            pg_extras.execute_values(
                cur,
                insert_sql,
                rows_with_rec,
                page_size=100,
            )

            conn.commit()
            logger.info("Inserted %d samples (recording=%s)", len(rows), recording_id)

        except Exception:
            if conn:
                conn.rollback()
            logger.exception("DB insert failed")
        finally:
            if conn:
                conn.close()

    except Exception:
        logger.exception("Error processing message: %s", payload)

# -------------------------------------------------
# Runner
# -------------------------------------------------
def run(broker_host, broker_port, topic, qos=0, username=None, password=None, client_id=None):
    userdata = {"topic": topic, "qos": qos}
    client = mqtt.Client(client_id=client_id, userdata=userdata)

    if username:
        client.username_pw_set(username, password or "")

    client.on_connect = on_connect
    client.on_message = on_message

    stop = {"flag": False}

    def _signal_handler(signum, frame):
        stop["flag"] = True
        logger.info("Stopping...")
        try:
            client.disconnect()
        except Exception:
            pass

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    backoff = 1
    while not stop["flag"]:
        try:
            client.connect(broker_host, broker_port, keepalive=60)
            client.loop_start()
            while not stop["flag"]:
                time.sleep(1)
            client.loop_stop()
            break
        except Exception as e:
            logger.error("MQTT error: %s. Reconnecting in %s s", e, backoff)
            time.sleep(backoff)
            backoff = min(30, backoff * 2)

# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    run(
        broker_host="127.0.0.1",
        broker_port=1883,
        topic="raw",
        qos=1,
        username="guest",
        password="guest",
        client_id="zcript",
    )
