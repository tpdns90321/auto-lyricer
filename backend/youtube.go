package main

import (
	"context"
	"io"
	"log"
	"os"

	"github.com/kkdai/youtube/v2"
	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
	ffmpeg "github.com/u2takey/ffmpeg-go"
)

type TranscriptorOption struct {
	Language *string
}

func (option *TranscriptorOption) SetLanguage(language string) {
	option.Language = &language
}

type Transcriptor interface {
	Transcription(ctx context.Context, data []byte, option *TranscriptorOption) (string, error)
}

func youtubePipelineWorker(app *pocketbase.PocketBase) {
	whisperClient, err := initializeRunpodWhisperClient()
	var transcriptor Transcriptor = whisperClient

	if err != nil {
		log.Println(err)
	}

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
		if err != nil {
			log.Println(err)
			continue
		}

		var url string
		if videoRecord.VideoID != "" {
			url = "https://youtube.com/watch?v=" + videoRecord.VideoID
		} else {
			continue
		}

		video, err := client.GetVideo(url)
		if err != nil {
			log.Println(err)
			continue
		}

		ctx := context.Background()
		done := make(chan error)

		go func() {
			defer func() {
				done <- nil
			}()

			formats := video.Formats.Quality("medium")
			videoFilePath := "/tmp/" + video.ID + ".mp4"
			musicFilePath := "/tmp/" + video.ID + ".mp3"

			// iterate video quaility for finding video that include audio
			for _, format := range formats {
				youtubeStream, _, err := client.GetStreamContext(ctx, video, &format)

				videoFile, err := os.Create(videoFilePath)
				defer func() {
					os.Remove(videoFilePath)
					videoFile.Close()
				}()

				if err != nil {
					log.Println(err)
					continue
				}

				io.Copy(videoFile, youtubeStream)
				err = ffmpeg.Input(videoFilePath).Output(musicFilePath).Run()

				if err != nil {
					log.Println(err)
					continue
				}

				break
			}

			musicFile, err := os.Open(musicFilePath)
			defer func() {
				musicFile.Close()
				os.Remove(musicFilePath)
			}()

			if err != nil {
				done <- err
				return
			}
			music, err := io.ReadAll(musicFile)
			if err != nil {
				done <- err
				return
			}

			transcriptorOption := TranscriptorOption{}
			if videoRecord.Language != "" {
				transcriptorOption.SetLanguage(videoRecord.Language)
			}
			data, err := transcriptor.Transcription(ctx, music, &transcriptorOption)
			if err != nil {
				done <- err
				return
			}
			videoRecord.Transcription = data
		}()

		err = <-done
		if err != nil {
			log.Println(err)
			continue
		}

		videoRecord.Title = video.Title
		videoRecord.Author = video.Author

		videoRecord.Update()
		app.Dao().SaveRecord(videoRecord.Record)
	}
}
