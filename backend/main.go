package main

import (
	"log"

	"github.com/joho/godotenv"
	"github.com/pocketbase/pocketbase"
)

func main() {
	godotenv.Load()
	app := pocketbase.New()

	go youtubePipelineWorker(app)
	go lyricsPipelineWorker(app)
	go transcriptionsPipelineWorker(app)

	if err := app.Start(); err != nil {
		log.Fatal(err)
	}
}
