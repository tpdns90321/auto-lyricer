package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"

	"github.com/gorilla/websocket"
	ffmpeg "github.com/u2takey/ffmpeg-go"
)

type RealtimeGPT4oClient struct {
	token string
}

type RealtimeGPT4oTranscriptionRequestContent struct {
	Type  string `json:"type"`
	Audio string `json:"audio"`
}

type RealtimeGPT4oTranscriptionRequestItem struct {
	Type    string                                     `json:"type"`
	Role    string                                     `json:"role"`
	Content []RealtimeGPT4oTranscriptionRequestContent `json:"content"`
}

type RealtimeGPT4oTranscriptionRequestItemCreate struct {
	Type string                                `json:"type"`
	Item RealtimeGPT4oTranscriptionRequestItem `json:"item"`
}

type RealtimeGPT4oTranscriptionRequestResponseCreate struct {
	Type     string                                   `json:"type"`
	Response RealtimeGPT4oTranscriptionResponseConfig `json:"response"`
}

type RealtimeGPT4oTranscriptionResponseConfig struct {
	Modalities   []string `json:"modalities"`
	Instructions *string  `json:"instructions"`
}

type RealtimeGPT4oTranscriptionResponseContent struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type RealtimeGPT4oTranscriptionResponseOutput struct {
	Content []RealtimeGPT4oTranscriptionResponseContent `json:"content"`
}

type RealtimeGPT4oTranscriptionResponseOutputList struct {
	Output []RealtimeGPT4oTranscriptionResponseOutput `json:"output"`
}

type RealtimeGPT4oTranscriptionResponse struct {
	Type     string                                       `json:"type"`
	Response RealtimeGPT4oTranscriptionResponseOutputList `json:"response"`
}

func initializeRealtimeGPT4oClient() (*RealtimeGPT4oClient, error) {
	token := os.Getenv("OPENAI_API_KEY")
	if token != "" {
		return &RealtimeGPT4oClient{token: token}, nil
	}

	return nil, errors.New("Invalid token")
}

func (client *RealtimeGPT4oClient) Transcription(_ context.Context, file []byte, option *TranscriptorOption) (string, error) {
	if client.token == "" {
		return "", errors.New("Invalid token")
	}

	// convert 작업 후 생각
	wavConvertedBuffer := bytes.NewBuffer(nil)
	err := ffmpeg.
		Input("pipe:", ffmpeg.KwArgs{"format": "mp3"}).
		WithInput(bytes.NewReader(file)).
		Output("pipe:", ffmpeg.KwArgs{"format": "wav", "ac": 1, "ar": 8000, "codec": "pcm_alaw"}).
		WithOutput(wavConvertedBuffer, os.Stdout).
		Run()
	if err != nil {
		return "", err
	}

	wavConverted, _ := io.ReadAll(wavConvertedBuffer)
	base64Converted := make([]byte, base64.StdEncoding.EncodedLen(len(wavConverted)))
	base64.StdEncoding.Encode(base64Converted, wavConverted)

	u := url.URL{Scheme: "wss", Host: "api.openai.com", Path: "/v1/realtime", RawQuery: "model=gpt-4o-realtime-preview"}
	conn, httpRes, err := websocket.DefaultDialer.Dial(
		u.String(),
		http.Header{
			"Authorization": []string{"Bearer " + client.token},
			"OpenAI-Beta":   []string{"realtime=v1"},
		},
	)
	if err != nil {
		body, _ := io.ReadAll(httpRes.Body)
		log.Println(string(body), httpRes.Status, httpRes.Header)
		return "", fmt.Errorf("Websocket Dial: %w", err)
	}
	defer conn.Close()

	done := make(chan *RealtimeGPT4oTranscriptionResponse)
	errDone := make(chan error)
	go func() {
		instructions := `Describe this audio clip into below SRT format:
{num}
{hh:mm:ss,mmm start time} --> {hh:mm:ss,mmm end time}
{transcription only voice}`
		base64ConvertedString := string(base64Converted)
		itemCreate := RealtimeGPT4oTranscriptionRequestItemCreate{
			Type: "conversation.item.create",
			Item: RealtimeGPT4oTranscriptionRequestItem{
				Type: "message",
				Role: "user",
				Content: []RealtimeGPT4oTranscriptionRequestContent{
					{
						Type:  "input_audio",
						Audio: base64ConvertedString,
					},
				},
			},
		}
		err = conn.WriteJSON(itemCreate)
		if err != nil {
			errDone <- err
			return
		}

		err = conn.WriteJSON(RealtimeGPT4oTranscriptionRequestResponseCreate{
			Type: "response.create",
			Response: RealtimeGPT4oTranscriptionResponseConfig{
				Modalities:   []string{"text"},
				Instructions: &instructions,
			},
		})
		if err != nil {
			errDone <- err
			return
		}

		for {
			var response RealtimeGPT4oTranscriptionResponse
			_, responseText, err := conn.ReadMessage()
			if err != nil {
				errDone <- err
				return
			}
			log.Println(string(responseText))

			err = json.Unmarshal(responseText, &response)
			if err != nil {
				errDone <- err
				return
			}

			if response.Type == "response.done" {
				done <- &response
				return
			}
		}
	}()

	select {
	case response := <-done:
		Outputs := response.Response.Output
		log.Println(response)
		return Outputs[0].Content[0].Text, nil
	case err := <-errDone:
		return "", err
	}

	//	responseBodyBinary, _ := io.ReadAll(res.Body)
	//	if res.StatusCode != http.StatusOK {
	//		return "", errors.New("Invalid response")
	//	}

	// var responseBody RealtimeGPT4oTranscriptionResponse
	//
	//	if err := json.Unmarshal(responseBodyBinary, &responseBody); err != nil {
	//		return "", err
	//	} else {
	//
	//		return responseBody.Output.Transcription, nil
	//	}
}
