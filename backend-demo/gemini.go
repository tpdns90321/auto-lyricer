package main

import (
	"context"
	"log"
	"os"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

type GeminiClient struct {
	apiKey string
}

func intializeGeminiClient() (*GeminiClient, error) {
	geminiCredential := os.Getenv("GEMINI_API_KEY")

	return &GeminiClient{apiKey: geminiCredential}, nil
}

func NewGeminiClient() (*GeminiClient, error) {
	return intializeGeminiClient()
}

func (c *GeminiClient) TextComplete(ctx context.Context, messages []Message, options ComplectionOption) (string, error) {
	client, err := genai.NewClient(ctx, option.WithAPIKey(c.apiKey))
	if err != nil {
		return "", err
	}
	defer client.Close()

	responseAggreation := ""

	model := client.GenerativeModel(options.Model)
	model.SetTemperature(*options.Temperature)
	model.SetMaxOutputTokens(int32(*options.MaxTokens))
	model.StopSequences = options.StopWords
	model.ResponseMIMEType = "text/plain"

	for {
		inputs := make([]*genai.Content, len(messages)-1)

		for i, m := range messages[:len(messages)-1] {
			msg := &inputs[i]

			switch m.(type) {
			case *AssistatntMessage:
				*msg = &genai.Content{
					Role: "model",
					Parts: []genai.Part{
						genai.Text(*m.Content()),
					},
				}
			case *UserMessage:
				*msg = &genai.Content{
					Role: "user",
					Parts: []genai.Part{
						genai.Text(*m.Content()),
					},
				}
			}
		}
		session := model.StartChat()
		session.History = inputs

		currentInput := genai.Text(*messages[len(messages)-1].Content())
		response, err := session.SendMessage(ctx, currentInput)
		if err != nil {
			return "", err
		}

		responseText, ok := response.Candidates[0].Content.Parts[0].(genai.Text)
		if !ok {
			return "", nil
		}
		responseAggreation += string(responseText)

		if response.Candidates[0].FinishReason != genai.FinishReasonMaxTokens {
			log.Println(response.Candidates[0].FinishReason.String())
			return responseAggreation, nil
		}

		log.Println(response.Candidates[0].Content.Parts[0])

		messages = append(messages, &AssistatntMessage{string(responseText)})
	}
}
