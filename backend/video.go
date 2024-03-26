package main

import (
  "errors"

  "github.com/pocketbase/pocketbase/models"
)

type VideoData struct {
  VideoID string `json:"videoID"`
  Title string `json:"title"`
  Author string `json:"author"`
  Transcription string `json:"transcription"`
  Language string `json:"language"`
}

type VideoPocketBase struct {
  *models.Record
  *VideoData
}

func convertRecordToVideo(record *models.Record) (*VideoPocketBase, error) {
  if record == nil || record.Collection().Name != "videos" {
    return nil, errors.New("Invalid record")
  }

  video := &VideoPocketBase{
    Record: record,
    VideoData: &VideoData{},
  }

  video.VideoID = video.GetString("videoID")
  video.Title = video.GetString("title")
  video.Author = video.GetString("author")
  video.Transcription = video.GetString("transcription")

  return video, nil
}

func (video *VideoPocketBase) Update() {
  video.Set("videoID", video.VideoID)
  video.Set("title", video.Title)
  video.Set("author", video.Author)
  video.Set("transcription", video.Transcription)
  video.Set("language", video.Language)
}
