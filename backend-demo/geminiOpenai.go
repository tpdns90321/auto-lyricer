package main

import (
	"context"
	"log"
	"os"

	"github.com/Azure/azure-sdk-for-go/sdk/ai/azopenai"
	"github.com/Azure/azure-sdk-for-go/sdk/azcore"
)

type GeminiOpenaiClient struct {
	*azopenai.Client
}

func intializeGeminiOpenaiClient() (*GeminiOpenaiClient, error) {
	openaiCredential := azcore.NewKeyCredential(os.Getenv(("GEMINI_API_KEY")))
	client, err := azopenai.NewClientForOpenAI("https://generativelanguage.googleapis.com/v1beta/", openaiCredential, nil)
	if err != nil {
		return nil, err
	}

	return &GeminiOpenaiClient{Client: client}, nil
}

func NewGeminiOpenaiClient() (*GeminiOpenaiClient, error) {
	return intializeGeminiOpenaiClient()
}

func (c *GeminiOpenaiClient) TextComplete(ctx context.Context, messages []Message, option ComplectionOption) (string, error) {
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

	responseAggreation := ""

	for {
		response, err := c.Client.GetChatCompletions(ctx, azopenai.ChatCompletionsOptions{
			Messages:       inputs,
			Stop:           option.StopWords,
			Temperature:    option.Temperature,
			TopP:           option.TopP,
			DeploymentName: &option.Model,
		}, nil)

		if err != nil {
			return "", err
		}

		responseAggreation += *response.Choices[0].Message.Content
		if *response.Choices[0].FinishReason != azopenai.CompletionsFinishReasonTokenLimitReached {
			log.Println(response.Choices[0].FinishReason)
			return responseAggreation, nil
		}

		log.Println(response.Choices[0].Message.Content)
		log.Println(response.SystemFingerprint)

		inputs = append(inputs, &azopenai.ChatRequestAssistantMessage{Content: response.Choices[0].Message.Content})
	}
}
