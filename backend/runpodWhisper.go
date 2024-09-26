package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"os"
)

type RunpodWhisperClient struct {
	token    string
	endpoint string
}

type RunpodWhisperTranscriptionRequestInput struct {
	Audio         *string `json:"audio"`
	AudioBase64   *string `json:"audio_base64"`
	Model         string  `json:"model"`
	Transcription string  `json:"transcription"`
	Translate     bool    `json:"translate"`
	Language      *string `json:"language"`
	Temperature   float32 `json:"temperature"`
	BestOf        int     `json:"best_of"`
	BeamSize      int     `json:"beam_size"`
}

type RunpodWhisperTranscriptionRequestBody struct {
	Input     RunpodWhisperTranscriptionRequestInput `json:"input"`
	EnableVad bool                                   `json:"enable_vad"`
}

type RunpodWhisperTranscriptionResponseOutput struct {
	DetectedLangauge string `json:"detected_language"`
	Transcription    string `json:"transcription"`
	Translation      string `json:"translation"`
}

type RunpodWhisperTranscriptionResponse struct {
	Output RunpodWhisperTranscriptionResponseOutput `json:"output"`
}

func initializeRunpodWhisperClient() (*RunpodWhisperClient, error) {
	token := os.Getenv("RUNPOD_WHISPER_API_KEY")
	endpoint := os.Getenv("RUNPOD_WHISPER_ENDPOINT")
	if token != "" && endpoint != "" {
		return &RunpodWhisperClient{token: token, endpoint: endpoint}, nil
	}

	return nil, errors.New("Invalid token")
}

func (client *RunpodWhisperClient) Transcription(_ context.Context, file []byte, option *TranscriptorOption) (string, error) {
	if client.token == "" {
		return "", errors.New("Invalid token")
	}

	audioBase64 := base64.StdEncoding.EncodeToString(file)
	requestBody := &RunpodWhisperTranscriptionRequestBody{
		Input: RunpodWhisperTranscriptionRequestInput{
			AudioBase64:   &audioBase64,
			Model:         "large-v3",
			Transcription: "srt",
			Temperature:   0.775,
			BestOf:        5,
			BeamSize:      10,
			Language:      option.Language,
		},
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", client.endpoint+"/runsync", bytes.NewReader(jsonBody))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", client.token)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	res, err := http.DefaultClient.Do(req)
	defer req.Body.Close()

	if err != nil {
		return "", err
	}

	responseBodyBinary, _ := io.ReadAll(res.Body)
	if res.StatusCode != http.StatusOK {
		return "", errors.New("Invalid response")
	}

	var responseBody RunpodWhisperTranscriptionResponse
	if err := json.Unmarshal(responseBodyBinary, &responseBody); err != nil {
		return "", err
	} else {
		return responseBody.Output.Transcription, nil
	}
}
