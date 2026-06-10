package controller

import (
	"eeg/internal/models"
	"eeg/internal/repository"
	"log"
	"net/http"
	"strconv"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/labstack/echo/v4"
)

type RecordingController struct {
	queries *repository.Queries
}

func NewRecordingController(queries *repository.Queries) *RecordingController {
	return &RecordingController{queries: queries}
}

func (r *RecordingController) GetAllRecordings() echo.HandlerFunc {
	return func(c echo.Context) error {
		recordings, err := r.queries.GetAllRecordings(c.Request().Context())
		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}
		data := make([]models.Recording, len(recordings))
		for i, v := range recordings {
			data[i] = models.Recording{
				Id:               int(v.ID),
				UserId:           int(v.UserID),
				TimeFrom:         v.TimeFrom.Time,
				TimeTo:           v.TimeTo.Time,
				StatePrediction:  v.StatePrediction,
				ActionPrediction: v.ActionPrediction,
			}
			user, err := r.queries.GetUserByID(c.Request().Context(), v.UserID)
			if err == nil {
				data[i].User = models.User{
					Id:        int(user.ID),
					FirstName: user.FirstName,
					LastName:  user.LastName,
				}
			} else {
				log.Printf("couldnt get user info: %v", err.Error())
			}
		}

		return c.JSON(http.StatusOK, data)
	}
}

func (r *RecordingController) SubmitRecording() echo.HandlerFunc {
	return func(c echo.Context) error {
		recording := new(models.Recording)

		if err := c.Bind(recording); err != nil {
			log.Println(err.Error())
			return c.JSON(http.StatusBadRequest, echo.Map{"error": "invalid recording data"})
		}

		reqParams := repository.SubmitRecordingParams{
			UserID:   int32(recording.UserId),
			TimeFrom: pgtype.Timestamp{Time: recording.TimeFrom, Valid: true},
			TimeTo:   pgtype.Timestamp{Time: recording.TimeTo, Valid: true},
		}
		rec, err := r.queries.SubmitRecording(c.Request().Context(), reqParams)

		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}

		data := make([]repository.InsertSamplesParams, len(recording.Samples))

		for i, v := range recording.Samples {
			data[i] = repository.InsertSamplesParams{
				TimeStamp:   pgtype.Timestamp{Time: v.Time, Valid: true},
				Eeg1:        v.Eeg1,
				Eeg2:        v.Eeg2,
				Ecg:         v.Ecg,
				RecordingID: rec.ID,
			}

			recording.Samples[i].RecordingId = int(rec.ID)
		}

		log.Println(recording)

		_, err = r.queries.InsertSamples(c.Request().Context(), data)
		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}

		recording.Id = int(rec.ID)
		return c.JSON(http.StatusCreated, recording)
	}
}

func (r *RecordingController) GetRecordingByID() echo.HandlerFunc {
	return func(c echo.Context) error {
		idRaw := c.Param("id")
		id, err := strconv.Atoi(idRaw)
		if err != nil {
			return c.JSON(http.StatusBadRequest, echo.Map{"error": "invalid recording ID"})
		}

		rec, err := r.queries.GetRecordingByID(c.Request().Context(), int32(id))
		if err != nil {
			return c.JSON(http.StatusNotFound, echo.Map{"error": "recording not found"})
		}

		samples, err := r.queries.GetSamplesByRecordingID(c.Request().Context(), int32(id))

		ret := models.Recording{
			Id:               int(rec.ID),
			UserId:           int(rec.UserID),
			TimeFrom:         rec.TimeFrom.Time,
			TimeTo:           rec.TimeTo.Time,
			StatePrediction:  rec.StatePrediction,
			ActionPrediction: rec.ActionPrediction,
		}

		if err == nil {
			s := make([]models.Sample, len(samples))
			for i, v := range samples {
				s[i] = models.Sample{
					RecordingId: int(v.RecordingID),
					Time:        v.TimeStamp.Time,
					Eeg1:        v.Eeg1,
					Eeg2:        v.Eeg2,
					Ecg:         v.Ecg,
				}
			}
			ret.Samples = s
		} else {
			log.Printf("couldnt get samples: %v", err.Error())
		}

		user, err := r.queries.GetUserByID(c.Request().Context(), rec.UserID)
		if err == nil {
			ret.User = models.User{
				Id:        int(user.ID),
				FirstName: user.FirstName,
				LastName:  user.LastName,
			}
		} else {
			log.Printf("couldnt get user info: %v", err.Error())
		}

		return c.JSON(http.StatusOK, ret)
	}
}
