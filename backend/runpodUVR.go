package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type RunpodUVRClient struct {
	token    string
	endpoint string
}

type RunpodUVRRequestInput struct {
	Audio *string `json:"audio"`
}

type RunpodUVRRequestBody struct {
	Input RunpodUVRRequestInput `json:"input"`
}

type RunpodUVRResponseOutput struct {
	Vocals string `json:"vocals"`
}

type RunpodUVRResponse struct {
	Output RunpodUVRResponseOutput `json:"output"`
}

func initializeRunpodUVRClient() (*RunpodUVRClient, error) {
	token := os.Getenv("RUNPOD_WHISPER_API_KEY")
	endpoint := os.Getenv("RUNPOD_UVR_ENDPOINT")
	if token != "" && endpoint != "" {
		return &RunpodUVRClient{token: token, endpoint: endpoint}, nil
	}

	return nil, errors.New("Invalid token")
}

func (client *RunpodUVRClient) extractOnlyVocal(_ context.Context, file []byte) (string, error) {
	if client.token == "" {
		return "", errors.New("Invalid token")
	}

	audioBase64 := base64.StdEncoding.EncodeToString(file)
	requestBody := &RunpodUVRRequestBody{
		Input: RunpodUVRRequestInput{
			Audio: &audioBase64,
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

	httpClient := http.Client{
		Timeout: time.Minute * 4,
	}
	res, err := httpClient.Do(req)
	defer req.Body.Close()

	if err != nil {
		return "", err
	}

	responseBodyBinary, err := io.ReadAll(res.Body)
	if err != nil || res.StatusCode != http.StatusOK {
		return "", errors.New(
			fmt.Sprintf("Invalid response: %s", err.Error()))
	}

	var responseBody RunpodUVRResponse
	if err := json.Unmarshal(responseBodyBinary, &responseBody); err != nil {
		return "", err
	} else {
		return responseBody.Output.Vocals, nil
	}
}
