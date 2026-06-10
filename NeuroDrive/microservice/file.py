import psycopg2
from datetime import datetime, timedelta
import random

DB_CONFIG = {
    "dbname": "eeg",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": 5432
}

NUM_RECORDINGS = 5
SAMPLES_PER_RECORDING = 150
USER_ID = 1
SAMPLE_INTERVAL_MS = 20  # 50 Hz

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        for r in range(NUM_RECORDINGS):
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(
                milliseconds=SAMPLES_PER_RECORDING * SAMPLE_INTERVAL_MS
            )

            cur.execute(
                """
                INSERT INTO recordings (time_from, time_to, state_prediction, action_prediction, user_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    start_time,
                    end_time,
                    random.choice(["alert", "drowsy", "stressed"]),
                    random.choice(["cruise", "turn", "stop"]),
                    USER_ID
                )
            )

            recording_id = cur.fetchone()[0]

            samples = []
            ts = start_time
            for _ in range(SAMPLES_PER_RECORDING):
                samples.append((
                    ts,
                    random.uniform(5.0, 50.0),    # eeg1
                    random.uniform(5.0, 50.0),    # eeg2
                    random.uniform(60.0, 100.0),  # ecg
                    recording_id
                ))
                ts += timedelta(milliseconds=SAMPLE_INTERVAL_MS)

            cur.executemany(
                """
                INSERT INTO samples (time_stamp, eeg1, eeg2, ecg, recording_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                samples
            )

        conn.commit()
        print("Inserted 5 recordings with 150 samples each successfully.")

    except Exception as e:
        conn.rollback()
        print("Error:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
