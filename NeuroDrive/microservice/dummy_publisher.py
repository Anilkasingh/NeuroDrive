#!/usr/bin/env python3
"""
Dummy MQTT publisher to send synthetic EEG/ECG samples to the `raw` topic
in the same payload format consumed by main.py.

Usage:
  python dummy_publisher.py --host 127.0.0.1 --port 1883 --topic raw
"""

import argparse
import math
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt


def make_payload(n_samples: int):
    parts = ["hdr"]
    for i in range(n_samples):
        t = i / 50.0
        eeg1 = 100 * math.sin(2 * math.pi * 1.0 * t) + random.uniform(-5, 5)
        eeg2 = 90 * math.sin(2 * math.pi * 1.2 * t + 0.5) + random.uniform(-5, 5)
        ecg = 1000 + 50 * math.sin(2 * math.pi * 1.0 * t) + random.uniform(-10, 10)
        parts.append(f"{eeg1:.2f}|{eeg2:.2f}|{ecg:.2f}")

    # add hh:mm:ss timestamp to the last entry
    ts = datetime.now().strftime("%H:%M:%S")
    parts[-1] = parts[-1] + ";" + ts
    return ",".join(parts)


def publish_once(host, port, topic, samples=150, qos=1, keepalive=60):
    client = mqtt.Client()
    # default credentials for broker (can be overridden by args)
    # caller should call client.username_pw_set() if credentials are required
    client.connect(host, port, keepalive)
    payload = make_payload(samples)
    rc = client.publish(topic, payload, qos=qos)
    rc.wait_for_publish()
    client.disconnect()
    print(f"Published {samples} samples to {topic} on {host}:{port}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--topic", default="raw")
    p.add_argument("--samples", type=int, default=150)
    p.add_argument("--qos", type=int, default=1)
    p.add_argument("--username", default="guest", help="MQTT username (default: guest)")
    p.add_argument("--password", default="guest", help="MQTT password (default: guest)")
    args = p.parse_args()

    # set up client with credentials
    def publish_with_auth():
        client = mqtt.Client()
        if args.username is not None:
            client.username_pw_set(args.username, args.password or "")
        client.connect(args.host, args.port, args.samples)
        payload = make_payload(args.samples)
        rc = client.publish(args.topic, payload, qos=args.qos)
        rc.wait_for_publish()
        client.disconnect()
        print(f"Published {args.samples} samples to {args.topic} on {args.host}:{args.port} (user={args.username})")

    publish_with_auth()
