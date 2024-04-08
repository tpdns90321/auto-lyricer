package main

import (
  "log"

  "github.com/pocketbase/pocketbase"
)

func main() {
  app := pocketbase.New()

  go youtubePipelineWorker(app)
  go lyricsPipelineWorker(app)

  if err := app.Start(); err != nil {
    log.Fatal(err)
  }
}
