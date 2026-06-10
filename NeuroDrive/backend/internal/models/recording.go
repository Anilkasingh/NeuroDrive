package models

import "time"

type Recording struct {
	Id               int       `json:"id"`
	TimeFrom         time.Time `json:"timeFrom"`
	TimeTo           time.Time `json:"timeTo"`
	UserId           int       `json:"userId"`
	StatePrediction  string    `json:"state_prediction"`
	ActionPrediction string    `json:"action_prediction"`
	Samples          []Sample  `json:"samples"`
	User             User      `json:"user"`
}
