package main

import (
	"context"
  "log"
	"io"
	"os"
	"sync"

	"github.com/kkdai/youtube/v2"
	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
	"github.com/u2takey/ffmpeg-go"
)

type Transcriptor interface {
  Transcription(ctx context.Context, data []byte) (string, error)
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
    go func () {
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

    wg := sync.WaitGroup{}
    wg.Add(1)

    go func() {
      defer wg.Done()
      formats := video.Formats.Quality("medium")
      // first format is video only, second format is video with audio
      youtubeStream, _, err := client.GetStreamContext(ctx, video, &formats[1])

      videoFilePath := "/tmp/" + video.ID + ".mp4"
      musicFilePath := "/tmp/" + video.ID + ".mp3"

      videoFile, err := os.Create(videoFilePath)
      defer func() {
        os.Remove(videoFilePath)
        videoFile.Close()
      }()

      if err != nil {
        log.Println(err)
        return
      }

      io.Copy(videoFile, youtubeStream)

      err = ffmpeg_go.Input(videoFilePath).Output(musicFilePath).Run()
      if err != nil {
        log.Println(err)
        return
      }

      musicFile, err := os.Open(musicFilePath)
      defer func() {
        musicFile.Close()
        os.Remove(musicFilePath)
      }()

      if err != nil {
        log.Println(err)
        return
      }

      if music, err := io.ReadAll(musicFile); err == nil {
        data, err := transcriptor.Transcription(ctx, music)
        if err == nil {
          videoRecord.Transcription = data
        } else {
          log.Println(err)
        }
      } else {
        log.Println(err)
      }
    }()

    videoRecord.Title = video.Title
    videoRecord.Author = video.Author

    wg.Wait()
    videoRecord.Update()
    app.Dao().SaveRecord(videoRecord.Record)
  }
}
