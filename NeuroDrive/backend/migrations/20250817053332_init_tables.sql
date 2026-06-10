-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query';

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL
);

CREATE TABLE recordings (
    id SERIAL PRIMARY KEY,
    time_from TIMESTAMP NOT NULL,
    time_to TIMESTAMP NOT NULL,
    state_prediction VARCHAR,
    action_prediction VARCHAR,
    user_id INT NOT NULL REFERENCES users(id)
);

CREATE TABLE samples (
    time_stamp TIMESTAMP NOT NULL,
    eeg1 INT NOT NULL,
    eeg2 INT NOT NULL,
    ecg INT NOT NULL,
    recording_id INT NOT NULL REFERENCES recordings(id)
)
WITH (
    timescaledb.hypertable,
    timescaledb.partition_column=time_stamp,
    timescaledb.segmentby=recording_id
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query';
-- +goose StatementEnd
