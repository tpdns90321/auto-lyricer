package main

import (
	"context"
	"errors"
	"log"
	"os"

	"github.com/liushuangls/go-anthropic/v2"
)

type AnthropicClient struct {
	*anthropic.Client
}

func NewAnthrophicClient() (*AnthropicClient, error) {
	apiKey := os.Getenv(("ANTHROPIC_API_KEY"))

	if apiKey == "" {
		return nil, errors.New("ANTHROPIC_API_KEY is not set")
	}

	return &AnthropicClient{anthropic.NewClient(apiKey, anthropic.WithBetaVersion(anthropic.BetaMaxTokens35Sonnet20240715))}, nil
}

func (c *AnthropicClient) TextComplete(ctx context.Context, messages []Message, option ComplectionOption) (string, error) {
	inputs := make([]anthropic.Message, len(messages))

	for i, m := range messages {
		inputs[i].Content = make([]anthropic.MessageContent, 1)
		inputs[i].Content[0] = anthropic.NewTextMessageContent(*m.Content())

		switch m.(type) {
		case *AssistatntMessage:
			inputs[i].Role = "assistant"
		case *UserMessage:
			inputs[i].Role = "user"
		}
	}

	if option.MaxTokens == nil {
		option.MaxTokens = new(int)
		*option.MaxTokens = 4096
	}

	response, err := c.Client.CreateMessages(ctx, anthropic.MessagesRequest{
		Model:         anthropic.Model(option.Model),
		System:        option.SystemPrompt,
		Messages:      inputs,
		StopSequences: option.StopWords,
		MaxTokens:     *option.MaxTokens,
		Temperature:   option.Temperature,
		TopP:          option.TopP,
		TopK:          option.TopK,
	})

	if err != nil {
		return "", err
	}

	log.Println(response.Content)
	log.Println(response.StopReason)

	return response.GetFirstContentText(), nil
}
