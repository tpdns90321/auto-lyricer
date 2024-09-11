package main

import (
	"context"
	"log"
	"os"

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

	return &OpenAIClient{Client: client}, nil
}

func NewOpenAIClient() (*OpenAIClient, error) {
	return intializeOpenAIClient()
}

func (client *OpenAIClient) Transcription(ctx context.Context, file []byte) (string, error) {
	whisperDeploymentName := "whisper-1"
	responseFormat := azopenai.AudioTranscriptionFormatSrt
	temperature := float32(0.5)

	body := azopenai.AudioTranscriptionOptions{
		File:           file,
		DeploymentName: &whisperDeploymentName,
		ResponseFormat: &responseFormat,
		Temperature:    &temperature,
	}

	transcription, err := client.GetAudioTranscription(ctx, body, nil)

	if err != nil {
		empty := ""
		return empty, err
	}

	return *transcription.Text, nil
}

func (c *OpenAIClient) TextComplete(ctx context.Context, messages []Message, option ComplectionOption) (string, error) {
	inputs := make([]azopenai.ChatRequestMessageClassification, len(messages)+1)

	inputs[0] = &azopenai.ChatRequestSystemMessage{Content: &option.SystemPrompt}

	for i, m := range messages {
		msg := &inputs[i+1]

		switch m.(type) {
		case *AssistatntMessage:
			*msg = &azopenai.ChatRequestAssistantMessage{Content: m.Content()}
		case *UserMessage:
			*msg = &azopenai.ChatRequestUserMessage{Content: azopenai.NewChatRequestUserMessageContent(*m.Content())}
		}
	}

	var maxTokens *int32 = nil
	if option.MaxTokens != nil {
		originalMaxTokens := *option.MaxTokens
		convertedMaxTokens := int32(originalMaxTokens)
		maxTokens = &convertedMaxTokens
	}

	response, err := c.Client.GetChatCompletions(ctx, azopenai.ChatCompletionsOptions{
		Messages:       inputs,
		Stop:           option.StopWords,
		MaxTokens:      maxTokens,
		Temperature:    option.Temperature,
		TopP:           option.TopP,
		DeploymentName: &option.Model,
	}, nil)

	if err != nil {
		return "", err
	}

	log.Println(response.Choices[0].Message.Content)
	log.Println(response.SystemFingerprint)

	return *response.Choices[0].Message.Content, nil
}
