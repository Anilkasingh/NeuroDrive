package models

import "time"

type Sample struct {
	Eeg1        float64   `json:"eeg1"`
	Eeg2        float64   `json:"eeg2"`
	Ecg         float64   `json:"ecg"`
	Time        time.Time `json:"time"`
	RecordingId int       `json:"recording_id"`
}
