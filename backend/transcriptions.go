package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"errors"
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

type TranscriptionData struct {
	VideoData     *VideoData `json:"video"`
	Language      string     `json:"language"`
	Transcription string     `json:"transcription"`
}

type TranscriptionPocketBase struct {
	*models.Record
	*TranscriptionData
	Video *VideoPocketBase
}

func convertRecordToTranscription(app *pocketbase.PocketBase, record *models.Record) (*TranscriptionPocketBase, error) {
	if record == nil || record.Collection().Name != "transcriptions" {
		return nil, errors.New("Invalid record")
	}

	transcription := &TranscriptionPocketBase{
		Record:            record,
		TranscriptionData: &TranscriptionData{},
	}

	if videoRecordId := record.GetString("video"); videoRecordId != "" {
		filterVideo, err := app.Dao().FindRecordsByIds("videos", []string{videoRecordId})
		if err != nil {
			return nil, err
		}

		video, err := convertRecordToVideo(filterVideo[0])
		if err != nil {
			return nil, err
		}

		transcription.Video = video
		transcription.VideoData = video.VideoData
	} else {
		return nil, errors.New("Invalid video record")
	}

	transcription.Language = transcription.GetString("language")
	transcription.Transcription = transcription.GetString("transcription")

	return transcription, nil
}

func (transcription *TranscriptionPocketBase) Update() {
	transcription.Set("video", transcription.Video.Id)
	transcription.Set("language", transcription.Language)
	transcription.Set("transcription", transcription.Transcription)
}

func transcriptionsPipelineWorker(app *pocketbase.PocketBase) {
	transcriptionPipeline := make(chan *models.Record)

	whisperClient, err := initializeRunpodWhisperClient()
	if err != nil {
		log.Println(err)
	}
	//  whisperClient, err := initializeRealtimeGPT4oClient()
	//  if err != nil {
	//    log.Println(err)
	//  }
	uvrClient, err := initializeRunpodUVRClient()
	if err != nil {
		log.Println(err)
	}
	youtubeClient := youtube.Client{}

	var transcriptor Transcriptor = whisperClient

	app.OnRecordAfterCreateRequest("transcriptions").Add((func(e *core.RecordCreateEvent) error {
		go func() {
			transcriptionPipeline <- e.Record
		}()

		return nil
	}))

	for {
		transcriptionRecord, err := convertRecordToTranscription(app, <-transcriptionPipeline)
		if err != nil {
			log.Println(err)
			continue
		}

		if transcriptionRecord.Transcription != "" {
			continue
		}

		if transcriptionRecord.VideoData == nil {
			continue
		}

		videoID := transcriptionRecord.VideoData.VideoID
		video, err := youtubeClient.GetVideo("https://youtube.com/watch?v=" + videoID)
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

			musicFile := []byte{}

			// iterate video quality for finding video that include audio
			for _, format := range formats {
				youtubeStream, _, err := youtubeClient.GetStreamContext(ctx, video, &format)
				if err != nil {
					log.Println(err)
					continue
				}

				musicStream := bytes.NewBuffer(nil)

				err = ffmpeg.
					Input("pipe:", ffmpeg.KwArgs{"format": "mp4"}).
					WithInput(youtubeStream).
					Output("pipe:", ffmpeg.KwArgs{"format": "mp3"}).
					WithOutput(musicStream, os.Stdout).
					Run()

				if err != nil {
					log.Println(err)
					continue
				}

				musicFile, _ = io.ReadAll(musicStream)

				break
			}

			vocalsBase64, err := uvrClient.extractOnlyVocal(ctx, musicFile)
			if err != nil {
				done <- err
				return
			}

			vocals := make([]byte, base64.StdEncoding.DecodedLen(len(vocalsBase64)))
			_, err = base64.StdEncoding.Decode(vocals, []byte(vocalsBase64))
			if err != nil {
				done <- err
				return
			}

			transcriptorOption := &TranscriptorOption{}
			if transcriptionRecord.Language != "" {
				transcriptorOption.SetLanguage(transcriptionRecord.Language)
			}
			data, err := transcriptor.Transcription(ctx, vocals, transcriptorOption)
			if err != nil {
				done <- err
				return
			}

			os.WriteFile("/tmp/"+videoID+"-vocals.mp3", vocals, 0644)

			transcriptionRecord.Transcription = data
		}()

		err = <-done
		if err != nil {
			log.Println(err)
			continue
		}

		transcriptionRecord.Update()
		app.Dao().SaveRecord(transcriptionRecord.Record)
	}
}
