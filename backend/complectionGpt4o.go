package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	//ffmpeg "github.com/u2takey/ffmpeg-go"
)

type ComplectionGPT4oClient struct {
	token string
}

type ComplectionGPT4oInputAudio struct {
	Data   string `json:"data"`
	Format string `json:"format"`
}

type ComplectionGPT4oContent struct {
	Type       string                      `json:"type"`
	InputAudio *ComplectionGPT4oInputAudio `json:"input_audio"`
	Text       string                      `json:"text"`
}

type ComplectionGPT4oMessage struct {
	Role    string                    `json:"role"`
	Content []ComplectionGPT4oContent `json:"content"`
}

type ComplectionGPT4oAudioConfig struct {
	Voice  string `json:"voice"`
	Format string `json:"format"`
}

type ComplectionGPT4oRequest struct {
	Model      string                      `json:"model"`
	Modalities []string                    `json:"modalities"`
	Messages   []ComplectionGPT4oMessage   `json:"messages"`
	Audio      ComplectionGPT4oAudioConfig `json:"audio"`
}

type ComplectionGPT4oChoice struct {
	Message ComplectionGPT4oMessage `json:"message"`
}

type ComplectionGPT4oResponse struct {
	Choices []ComplectionGPT4oChoice `json:"choices"`
}

func initializeComplectionGPT4oClient() (*ComplectionGPT4oClient, error) {
	token := os.Getenv("OPENAI_API_KEY")
	if token != "" {
		return &ComplectionGPT4oClient{token: token}, nil
	}

	return nil, errors.New("Invalid token")
}

func (client *ComplectionGPT4oClient) Transcription(_ context.Context, file []byte, option *TranscriptorOption) (string, error) {
	if client.token == "" {
		return "", errors.New("Invalid token")
	}

	//  compressedBuffer := bytes.NewBuffer(nil)
	//  err := ffmpeg.
	//    Input("pipe:", ffmpeg.KwArgs{"format": "mp3"}).
	//    WithInput(bytes.NewReader(file)).
	//    Output("pipe:", ffmpeg.KwArgs{"format": "mp3", "ac": 1, "b:a": "24k"}).
	//		WithOutput(compressedBuffer, os.Stdout).
	//		Run()

	//  compressed, err := io.ReadAll(compressedBuffer)
	//  if err != nil {
	//    return "", err
	//  }

	//	base64Converted := make([]byte, base64.StdEncoding.EncodedLen(len(compressed)))
	//	base64.StdEncoding.Encode(base64Converted, compressed)
	base64Converted := make([]byte, base64.StdEncoding.EncodedLen(len(file)))
	base64.StdEncoding.Encode(base64Converted, file)
	base64ConvertedString := string(base64Converted)

	u := url.URL{Scheme: "https", Host: "api.openai.com", Path: "/v1/chat/completions"}
	reqBody := ComplectionGPT4oRequest{
		Model: "gpt-4o-audio-preview",
		Audio: ComplectionGPT4oAudioConfig{
			Voice:  "alloy",
			Format: "wav",
		},
		Modalities: []string{"text", "audio"},
		Messages: []ComplectionGPT4oMessage{
			{
				Role: "user",
				Content: []ComplectionGPT4oContent{
					{
						Type: "audio",
						InputAudio: &ComplectionGPT4oInputAudio{
							Data:   base64ConvertedString,
							Format: "wav",
						},
					},
					{
						Type: "text",
						Text: "Transcribe this recording to SRT format. Do not speak.",
					},
				},
			},
		},
	}

	reqBodyBytes, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", u.String(), bytes.NewReader(reqBodyBytes))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", "Bearer "+client.token)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err
	}

	body, err := io.ReadAll(res.Body)
	log.Println(string(body))
	response := ComplectionGPT4oResponse{}
	err = json.Unmarshal(body, &response)
	if err != nil {
		return "", err
	}

	if len(response.Choices) == 0 {
		return "", errors.New("No response")
	}

	return response.Choices[len(response.Choices)-1].Message.Content[0].Text, nil
}
