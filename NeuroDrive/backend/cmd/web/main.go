package main

import (
	"context"
	"eeg/internal/controller"
	"eeg/internal/models"
	"eeg/internal/mq"
	"eeg/internal/repository"
	"encoding/json"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
)

func main() {
	conn, err := pgxpool.New(context.Background(), "postgres://postgres:password@localhost:5432/eeg")
	if err != nil {
		log.Fatalln(err.Error())
	}

	queries := repository.New(conn)

	userController := controller.NewUserController(queries)
	recordingController := controller.NewRecordingController(queries)
	// analysisController := controller.NewAnalysisController(queries)

	e := echo.New()

	setupRoutes(e, userController, recordingController)

	q, err := mq.NewMq("amqp://guest:guest@localhost:5672/", "recordings")
	if err != nil {
		log.Fatalln(err.Error())
	}
	defer q.Close()

	ctx, cancel := context.WithCancel(context.Background())
	wg := sync.WaitGroup{}

	wg.Add(1)
	go func() {
		defer wg.Done()
		c, err := q.ReadMessages()
		if err != nil {
			log.Println(err.Error())
			return
		}
		for {
			select {
			case <-ctx.Done():
				return
			case msg := <-c:
				recording := models.Recording{}
				if err := json.Unmarshal(msg.Body, &recording); err != nil {
					log.Println(err.Error())
					continue
				} else {
					samples := make([]repository.InsertSamplesParams, len(recording.Samples))
					for i, v := range recording.Samples {
						samples[i] = repository.InsertSamplesParams{
							TimeStamp: pgtype.Timestamp{Time: v.Time, Valid: true},
							Eeg1:      v.Eeg1,
							Eeg2:      v.Eeg2,
							Ecg:       v.Ecg,
						}
					}
					_, err := queries.InsertSamples(ctx, samples)
					if err != nil {
						log.Println(err.Error())
					}

					_, err = queries.SubmitRecording(ctx, repository.SubmitRecordingParams{
						TimeFrom:         pgtype.Timestamp{Time: recording.TimeFrom, Valid: true},
						TimeTo:           pgtype.Timestamp{Time: recording.TimeTo, Valid: true},
						StatePrediction:  recording.StatePrediction,
						ActionPrediction: recording.ActionPrediction,
						UserID:           int32(recording.UserId),
					})
					if err != nil {
						log.Println(err.Error())
					}
				}
			}
		}
	}()

	exit := make(chan os.Signal, 1)
	signal.Notify(exit, os.Interrupt, syscall.SIGTERM)

	wg.Add(1)
	go func() {
		<-exit
		e.Shutdown(context.Background())
		cancel()
		wg.Done()
	}()

	if err := e.Start("0.0.0.0:8080"); err != nil {
		log.Fatalln(err.Error())
	}
	wg.Wait()
}
