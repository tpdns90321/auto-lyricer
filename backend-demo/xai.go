package main

import (
	"context"
	"log"
	"os"

	"github.com/Azure/azure-sdk-for-go/sdk/ai/azopenai"
	"github.com/Azure/azure-sdk-for-go/sdk/azcore"
)

type XaiClient struct {
	*azopenai.Client
}

func intializeXaiClient() (*XaiClient, error) {
	openaiCredential := azcore.NewKeyCredential(os.Getenv(("XAI_API_KEY")))
	client, err := azopenai.NewClientForOpenAI("https://api.x.ai/v1", openaiCredential, nil)
	if err != nil {
		return nil, err
	}

	return &XaiClient{Client: client}, nil
}

func NewXaiClient() (*XaiClient, error) {
	return intializeXaiClient()
}

func (c *XaiClient) TextComplete(ctx context.Context, messages []Message, option ComplectionOption) (string, error) {
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
