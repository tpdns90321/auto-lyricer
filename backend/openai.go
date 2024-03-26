package main 

import (
  "os"
  "context"

  "github.com/Azure/azure-sdk-for-go/sdk/ai/azopenai"
  "github.com/Azure/azure-sdk-for-go/sdk/azcore"
)

type OpenAIClient struct {
  *azopenai.Client
}

func intializeOpenAIClient() (*OpenAIClient, error) {
  openaiCredential := azcore.NewKeyCredential(os.Getenv(("OPENAI_API_KEY")))
  client, err := azopenai.NewClientForOpenAI("https://api.openai.com/v1", openaiCredential, nil)
  if err != nil {
    return nil, err
  }

  return &OpenAIClient{ Client: client }, nil
}

func (client *OpenAIClient) Transcription(ctx context.Context, file []byte) (string, error) {
  whisperDeploymentName := "whisper-1"
  responseFormat := azopenai.AudioTranscriptionFormatSrt
  temperature := float32(0.5)

  body := azopenai.AudioTranscriptionOptions{
    File: file,
    DeploymentName: &whisperDeploymentName,
    ResponseFormat: &responseFormat,
    Temperature: &temperature,
  }

  transcription, err := client.GetAudioTranscription(ctx, body, nil)

  if err != nil {
    empty := ""
    return empty, err
  }

  return *transcription.Text, nil
}
