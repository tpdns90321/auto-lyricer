package main

import (
	"context"
	"errors"
	"log"
	"strings"

	"github.com/pocketbase/pocketbase"
	"github.com/pocketbase/pocketbase/core"
	"github.com/pocketbase/pocketbase/models"
)

type LyricsData struct {
	TranscriptionData *TranscriptionData `json:"transcription"`
	Plain             string             `json:"plain"`
	Debug             string             `json:"debug"`
	Srt               string             `json:"srt"`
	Language          string             `json:"language"`
	Referenced        *LyricsData        `json:"referenced"`
}

type LyricsPocketBase struct {
	*models.Record
	*LyricsData
	Transcription *TranscriptionPocketBase
	Referenced    *LyricsPocketBase
}

func convertRecordToLyrics(app *pocketbase.PocketBase, record *models.Record) (*LyricsPocketBase, error) {
	if record == nil || record.Collection().Name != "lyrics" {
		return nil, errors.New("Invalid record")
	}

	lyrics := &LyricsPocketBase{
		Record:     record,
		LyricsData: &LyricsData{},
	}

	if transcriptionRecordId := record.GetString("transcription"); transcriptionRecordId != "" {
		filterTranscription, err := app.Dao().FindRecordsByIds("transcriptions", []string{transcriptionRecordId})
		if err != nil {
			return nil, err
		}

		transcription, err := convertRecordToTranscription(app, filterTranscription[0])
		if err != nil {
			return nil, err
		}

		lyrics.Transcription = transcription
		lyrics.TranscriptionData = transcription.TranscriptionData
	}

	lyrics.Plain = lyrics.GetString("plain")
	lyrics.Debug = lyrics.GetString("debug")
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
	if lyrics.Transcription != nil {
		lyrics.Set("transcription", lyrics.Transcription.Record.Id)
	}
	lyrics.Set("plain", lyrics.Plain)
	lyrics.Set("debug", lyrics.Debug)
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

		log.Println(lyricsRecord.Referenced)
		if lyricsRecord.Referenced == nil && lyricsRecord.Transcription != nil && lyricsRecord.Plain != "" && lyricsRecord.Srt == "" {
			if response, err := syncPipeline(ctx, lyricsRecord.LyricsData); err == nil {
				lyricsRecord.Srt = response
				lyricsRecord.Update()
			} else {
				log.Println(err)
			}
		} else if lyricsRecord.Referenced != nil && lyricsRecord.Language != "" && lyricsRecord.Transcription == nil && lyricsRecord.Plain == "" && lyricsRecord.Srt == "" {
			if response, err := translatePipeline(ctx, lyricsRecord.LyricsData); err == nil {
				srt := strings.TrimPrefix(response, "```"+`xml
`)
				srt = strings.TrimPrefix(srt, "<Result>")
				lyricsRecord.Srt = srt
				lyricsRecord.Update()
			} else {
				log.Println(err)
			}
		}

		app.Dao().SaveRecord(lyricsRecord.Record)
	}
}
