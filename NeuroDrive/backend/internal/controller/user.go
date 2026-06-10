package controller

import (
	"eeg/internal/models"
	"eeg/internal/repository"
	"net/http"
	"strconv"

	"github.com/labstack/echo/v4"
)

type UserController struct {
	queries *repository.Queries
}

func NewUserController(queries *repository.Queries) *UserController {
	return &UserController{
		queries: queries,
	}
}

func (u *UserController) GetAllUsers() echo.HandlerFunc {
	return func(c echo.Context) error {
		users, err := u.queries.GetAllUsers(c.Request().Context())
		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}

		data := make([]models.User, len(users))
		for i, v := range users {
			data[i] = models.User{
				Id:        int(v.ID),
				FirstName: v.FirstName,
				LastName:  v.LastName,
			}
		}
		return c.JSON(http.StatusOK, data)
	}
}

func (u *UserController) GetUserByID() echo.HandlerFunc {
	return func(c echo.Context) error {
		idRaw := c.Param("id")
		id, err := strconv.Atoi(idRaw)
		if err != nil {
			return c.JSON(http.StatusBadRequest, echo.Map{"error": "invalid user ID"})
		}

		user, err := u.queries.GetUserByID(c.Request().Context(), int32(id))
		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}

		return c.JSON(http.StatusOK, user)
	}
}

func (u *UserController) CreateUser() echo.HandlerFunc {
	return func(c echo.Context) error {
		user := new(models.User)

		if err := c.Bind(user); err != nil {
			return c.JSON(http.StatusBadRequest, echo.Map{"error": "invalid user data"})
		}

		reqParams := repository.CreateUserParams{
			FirstName: user.FirstName,
			LastName:  user.LastName,
		}
		u, err := u.queries.CreateUser(c.Request().Context(), reqParams)

		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}
		return c.JSON(http.StatusCreated, u)
	}
}

func (u *UserController) UpdateUser() echo.HandlerFunc {
	return func(c echo.Context) error {
		user := new(models.User)

		if err := c.Bind(user); err != nil {
			return c.JSON(http.StatusBadRequest, echo.Map{"error": "invalid user data"})
		}

		reqParams := repository.UpdateUserParams{
			ID:        int32(user.Id),
			FirstName: user.FirstName,
			LastName:  user.LastName,
		}
		u, err := u.queries.UpdateUser(c.Request().Context(), reqParams)

		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}
		return c.JSON(http.StatusOK, u)
	}
}

func (u *UserController) DeleteUser() echo.HandlerFunc {
	return func(c echo.Context) error {
		idRaw := c.Param("id")
		id, err := strconv.Atoi(idRaw)

		if err != nil {
			return c.JSON(http.StatusBadRequest, echo.Map{"error": "invalid user ID"})
		}

		err = u.queries.DeleteUser(c.Request().Context(), int32(id))
		if err != nil {
			return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
		}
		return c.JSON(http.StatusNoContent, nil)
	}
}
