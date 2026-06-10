-- name: GetAllRecordings :many
SELECT * FROM recordings;

-- name: SubmitRecording :one
INSERT INTO recordings (time_from, time_to, user_id, state_prediction, action_prediction)
VALUES ($1, $2, $3, $4, $5)
RETURNING *;

-- name: InsertSamples :copyfrom
INSERT INTO samples (time_stamp, eeg1, eeg2, ecg, recording_id)
VALUES ($1, $2, $3, $4, $5);

-- name: GetSamplesByRecordingID :many
SELECT * FROM samples WHERE recording_id = $1 ORDER BY time_stamp;

-- name: GetSamplesByUserID :many
SELECT * FROM samples s
INNER JOIN recordings r ON r.id = s.recording_id WHERE r.user_id = $1
ORDER BY time_stamp;

-- name: GetRecordingByID :one
SELECT * FROM recordings WHERE id = $1;

-- name: ListRecordingsByUserID :many
SELECT * FROM recordings WHERE user_id = $1 ORDER BY time_from;

-- name: GetAllUsers :many
SELECT * FROM users;

-- name: CreateUser :one
INSERT INTO users (first_name, last_name)
VALUES ($1, $2)
RETURNING *;

-- name: GetUserByID :one
SELECT * FROM users WHERE id = $1;

-- name: UpdateUser :one
UPDATE users SET first_name = $1, last_name = $2 WHERE id = $3 RETURNING *;

-- name: DeleteUser :exec
DELETE FROM users WHERE id = $1;