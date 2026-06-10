package main

import (
	"eeg/internal/controller"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func setupRoutes(e *echo.Echo, userController *controller.UserController, recordingController *controller.RecordingController) {

	e.Use(middleware.CORS())
	e.Use(middleware.Logger())

	// Health check endpoint
	e.GET("/", func(c echo.Context) error {
		return c.String(200, "EEG Backend API - Running")
	})

	// User routes
	users := e.Group("/users")
	users.POST("", userController.CreateUser())
	users.GET("", userController.GetAllUsers())
	users.GET("/:id", userController.GetUserByID())
	users.PUT("/:id", userController.UpdateUser())
	users.DELETE("/:id", userController.DeleteUser())
	// users.GET("/analysis/:id", analysisController.RunAnalysisOnUser())

	// Recording routes
	recordings := e.Group("/recordings")
	recordings.GET("", recordingController.GetAllRecordings())
	recordings.POST("", recordingController.SubmitRecording())
	recordings.GET("/:id", recordingController.GetRecordingByID())
	// recordings.GET("/analysis/:id", analysisController.RunAnalysis())
}
