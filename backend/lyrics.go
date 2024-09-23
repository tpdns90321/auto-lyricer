package main

import (
	"context"
	"errors"
	"log"

	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
)

type LyricsData struct {
	VideoData  *VideoData  `json:"video"`
	Plain      string      `json:"plain"`
	Srt        string      `json:"srt"`
	Language   string      `json:"language"`
	Referenced *LyricsData `json:"referenced"`
}

type LyricsPocketBase struct {
	*models.Record
	*LyricsData
	Video      *VideoPocketBase
	Referenced *LyricsPocketBase
}

func convertRecordToLyrics(app *pocketbase.PocketBase, record *models.Record) (*LyricsPocketBase, error) {
	if record == nil || record.Collection().Name != "lyrics" {
		return nil, errors.New("Invalid record")
	}

	lyrics := &LyricsPocketBase{
		Record:     record,
		LyricsData: &LyricsData{},
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

		lyrics.Video = video
		lyrics.VideoData = video.VideoData
	} else {
		return nil, errors.New("Invalid video record")
	}

	lyrics.Plain = lyrics.GetString("plain")
	lyrics.Srt = lyrics.GetString("srt")
	lyrics.Language = lyrics.GetString("language")
	if referencedLyricsId := record.GetString("referenced"); referencedLyricsId != "" {
		filteredLyrics, err := app.Dao().FindRecordsByIds("lyrics", []string{referencedLyricsId})
		if err != nil {
			return nil, err
		}
		referenced, err := convertRecordToLyrics(app, filteredLyrics[0])
		if err == nil {
			lyrics.Referenced = referenced
			lyrics.LyricsData.Referenced = referenced.LyricsData
		}
	}

	return lyrics, nil
}

func (lyrics *LyricsPocketBase) Update() {
	lyrics.Set("video", lyrics.Video.Record.Id)
	lyrics.Set("plain", lyrics.Plain)
	lyrics.Set("srt", lyrics.Srt)
	lyrics.Set("language", lyrics.Language)
	if lyrics.Referenced != nil {
		lyrics.Set("referenced", lyrics.Referenced.Record.Id)
	}
}

func lyricsPipelineWorker(app *pocketbase.PocketBase) {
	lyricsPipeline := make(chan *models.Record)

	app.OnRecordAfterCreateRequest("lyrics").Add((func(e *core.RecordCreateEvent) error {
		go func() {
			lyricsPipeline <- e.Record
		}()
		return nil
	}))

	for {
		ctx := context.Background()
		lyricsRecord, err := convertRecordToLyrics(app, <-lyricsPipeline)
		if err != nil {
			log.Println(err)
			continue
		}

		if lyricsRecord.Plain != "" && lyricsRecord.Srt == "" {
			if srt, err := syncPipeline(ctx, lyricsRecord.LyricsData); err == nil {
				lyricsRecord.Srt = srt
				lyricsRecord.Update()
			} else {
				log.Println(err)
			}
		}

		app.Dao().SaveRecord(lyricsRecord.Record)
	}
}
