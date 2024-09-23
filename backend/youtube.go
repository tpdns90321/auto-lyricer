package main

import (
	"log"

	"github.com/kkdai/youtube/v2"
	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
)

func youtubePipelineWorker(app *pocketbase.PocketBase) {
	youtubePipeline := make(chan *models.Record)

	client := youtube.Client{}

	app.OnRecordAfterCreateRequest("videos").Add((func(e *core.RecordCreateEvent) error {
		go func() {
			youtubePipeline <- e.Record
		}()

		return nil
	}))

	for {
		videoRecord, err := convertRecordToVideo(<-youtubePipeline)
		go func() {
			if err != nil {
				log.Println(err)
				return
			}

			var url string
			if videoRecord.VideoID != "" {
				url = "https://youtube.com/watch?v=" + videoRecord.VideoID
			} else {
				return
			}

			video, err := client.GetVideo(url)
			if err != nil {
				log.Println(err)
				return
			}

			videoRecord.Title = video.Title
			videoRecord.Author = video.Author

			videoRecord.Update()
			app.Dao().SaveRecord(videoRecord.Record)
		}()
	}
}
