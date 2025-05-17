package main

import (
	"encoding/json"
	"log"
	"time"

	"github.com/ZaViBiS/grow/db"
	"github.com/gofiber/fiber/v3"
	"github.com/gofiber/fiber/v3/middleware/cors"
	"gorm.io/gorm"
)

func getForDurationHandler(durationSeconds int64, timeGap int, database *gorm.DB) fiber.Handler {
	return func(c fiber.Ctx) error {
		data, err := db.GetFor(database, time.Now().Unix()-durationSeconds, timeGap)
		if err != nil {
			return c.Status(500).SendString("db error")
		}

		jsonData, err := json.Marshal(data)
		if err != nil {
			return c.Status(500).SendString("json error")
		}

		return c.Send(jsonData)
	}
}

func main() {
	database, err := db.InitDB("data.sqlite3")
	if err != nil {
		log.Fatal("init db")
		panic(err)
	}

	app := fiber.New()
	app.Use(cors.New())

	app.Get("/", func(c fiber.Ctx) error {
		return c.SendString("hello, world")
	})

	app.Get("/last", func(c fiber.Ctx) error {
		data, err := db.GetLast(database)
		if err != nil {
			log.Fatal("error", err)
		}
		jsonData, err := json.Marshal(data)
		if err != nil {
			log.Fatal("err", err)
		}
		return c.Send(jsonData)
	})

	app.Get("/hour", getForDurationHandler(60*60, 1, database))
	app.Get("/day", getForDurationHandler(60*60*24, 5, database))
	app.Get("/week", getForDurationHandler(60*60*24*7, 10, database))
	app.Get("/month", getForDurationHandler(60*60*24*30, 30, database))
	app.Get("/year", getForDurationHandler(60*60*24*365, 60, database))
	app.Get("/all", getForDurationHandler(time.Now().Unix(), 1, database))

	app.Post("/put", func(c fiber.Ctx) error {
		var data db.Data
		if err := c.Bind().Body(&data); err != nil {
			return fiber.NewError(fiber.StatusBadRequest, "Invalid JSON")
		}
		if err := database.Create(&data).Error; err != nil {
			return fiber.NewError(fiber.StatusInternalServerError, "Failed to insert")
		}
		return c.JSON(fiber.Map{"status": "ok"})
	})

	log.Fatal(app.Listen("[::]:8000", fiber.ListenConfig{
		ListenerNetwork: "tcp6",
	}))
}
