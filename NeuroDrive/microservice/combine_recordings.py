from __future__ import annotations
import json
from pathlib import Path
from statistics import median
from typing import List, Optional, Tuple

from models import Sample, Recording


def _read_json_allow_comments(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    # strip // comments at start of lines to tolerate files with a file-path comment
    cleaned = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))
    return json.loads(cleaned)


def _series_to_timestamped_values(series: List[dict]) -> List[Tuple[Optional[float], float]]:
    out: List[Tuple[Optional[float], float]] = []
    for item in series:
        ts = item.get("timestamp")
        if ts is None:
            # some later entries only have "value"
            ts = None
        else:
            ts = float(ts)
        out.append((ts, float(item["value"])))
    return out


def _infer_missing_timestamps(values: List[Tuple[Optional[float], float]], default_dt: float = 0.004) -> List[float]:
    # compute typical delta from available timestamps
    timestamps = [ts for ts, _ in values if ts is not None]
    dt = default_dt
    if len(timestamps) >= 2:
        diffs = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:]) if t2 - t1 > 0]
        if diffs:
            dt = float(median(diffs))
    result: List[float] = []
    last_ts: Optional[float] = None
    for i, (ts, _) in enumerate(values):
        if ts is not None:
            last_ts = ts
            result.append(ts)
        else:
            # infer using last known timestamp or using index*dt if none known yet
            if last_ts is not None:
                last_ts = last_ts + dt
                result.append(last_ts)
            else:
                # no previous timestamp: assume starting at index 0
                inferred = i * dt
                last_ts = inferred
                result.append(inferred)
    return result


def load_series(path: Path) -> Tuple[List[float], List[float]]:
    data = _read_json_allow_comments(path)
    # many files use top-level "samples" key
    series = data.get("samples", data if isinstance(data, list) else [])
    ts_vals = _series_to_timestamped_values(series)
    timestamps = _infer_missing_timestamps(ts_vals)
    values = [v for _, v in ts_vals]
    # if lengths mismatch (shouldn't), pad values with last value
    if len(values) < len(timestamps):
        values += [values[-1]] * (len(timestamps) - len(values))
    return timestamps, values


def create_recording(eeg1_path: str, eeg2_path: str, ecg_path: str, recording_id: int = 1, user=None) -> Recording:
    p1 = Path(eeg1_path)
    p2 = Path(eeg2_path)
    p3 = Path(ecg_path)

    ts1, vals1 = load_series(p1)
    ts2, vals2 = load_series(p2)
    ts3, vals3 = load_series(p3)

    # choose a unified timeline: prefer the longest timestamps list, or fall back to eeg1
    timelines = [ts1, ts2, ts3]
    timeline = max(timelines, key=len)

    # helper to sample a series value by nearest index (clip)
    def value_at(values: List[float], idx: int) -> float:
        if idx < 0:
            return values[0]
        if idx >= len(values):
            return values[-1]
        return values[idx]

    samples: List[Sample] = []
    for i, ts in enumerate(timeline):
        v1 = value_at(vals1, i) if vals1 else 0.0
        v2 = value_at(vals2, i) if vals2 else 0.0
        v3 = value_at(vals3, i) if vals3 else 0.0
        samples.append(Sample(eeg1=v1, eeg2=v2, ecg=v3, time=str(ts), recording_id=recording_id))

    time_from = str(timeline[0]) if timeline else "0"
    time_to = str(timeline[-1]) if timeline else "0"

    return Recording(id=recording_id, time_from=time_from, time_to=time_to, user_id=0, samples=samples, user=user)


def recording_to_dict(rec: Recording) -> dict:
    def _serializable_user(u):
        if u is None:
            return None
        try:
            json.dumps(u)
            return u
        except TypeError:
            return str(u)

    return {
        "id": rec.id,
        "time_from": rec.time_from,
        "time_to": rec.time_to,
        "user_id": rec.user_id,
        "user": _serializable_user(rec.user),
        "samples": [
            {
                "eeg1": s.eeg1,
                "eeg2": s.eeg2,
                "ecg": s.ecg,
                "time": s.time,
                "recording_id": s.recording_id,
            }
            for s in rec.samples
        ],
    }


if __name__ == "__main__":
    # Example usage: adjust paths as needed
    recording = create_recording("eeg1.json", "eeg2.json", "ecg.json", recording_id=1, user=None)
    out_path = Path("recording.json")
    out_path.write_text(json.dumps(recording_to_dict(recording), indent=2), encoding="utf-8")
    print(f"Wrote recording to {out_path.resolve()}")