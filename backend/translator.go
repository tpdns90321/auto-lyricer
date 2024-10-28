package main

import (
	"context"
	"fmt"
	iso6391 "github.com/emvi/iso-639-1"
	"log"
)

const translatorTemplate = `Translate the provided lyrics into %s, but do not translate any foreign words present in the original lyrics; leave them as is. Format your response as SRT by separating each component in this order: number, timing, original lyrics line, its English pronunciation, and the %s translation. Make sure each trio is clearly separated. Write SRT into 'Result' XML tag. Here are the lyrics:
%s`

func translatePipeline(ctx context.Context, lyrics *LyricsData) (string, error) {
	//	chatAI, err := NewOpenAIClient()
	//	llmModel := "gpt-4o-mini-2024-07-18"
	//	maxTokens := 16384

	chatAI, err := NewGeminiClient()
	llmModel := "gemini-1.5-flash-002"
	maxTokens := 8192

	temperature := float32(0.2)
	language := iso6391.Name(lyrics.Language)

	if err != nil {
		log.Println(err)
	}

	messages := []Message{
		&UserMessage{fmt.Sprintf(translatorTemplate, language, language, lyrics.Referenced.Srt)},
		&AssistatntMessage{"<Result>"},
	}

	option := ComplectionOption{
		Model:     llmModel,
		StopWords: []string{"</Result>"},
		MaxTokens: &maxTokens,
	}

	option.SetTemperature(temperature)

	response, err := chatAI.TextComplete(ctx, messages, option)
	if err != nil {
		return "", err
	}

	return response, nil
}
