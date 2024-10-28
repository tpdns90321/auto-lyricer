package main

import (
	"context"
	"log"
)

func syncPipeline(ctx context.Context, lyrics *LyricsData) (string, error) {
	// claude-3-5-sonnet-20241022
	//	chatAI, err := NewAnthrophicClient()
	//  llmModel := "claude-3-5-sonnet-20241022"
	//	maxTokens := 8192
	//  temperature := float32(0.5)

	// openai GPT-4o
	//	chatAI, err := NewOpenAIClient()
	//	llmModel := "gpt-4o-2024-08-06"
	//	maxTokens := 16384
	//	temperature := float32(0.4)
	chatAI, err := NewGeminiClient()
	llmModel := "gemini-1.5-flash-002"
	maxTokens := 8192
	temperature := float32(0.2)

	if err != nil {
		log.Println(err)
	}

	messages := []Message{
		&UserMessage{`Repeat SRT through by each sequence with matching between each sequence and similar line of dialogues.
After repeating SRT, AI will summarize result as SRT with replaced dialogues.

<Example>
<Dialogues>
Chasing sunsets, on the horizon
Feel the breeze, in my hair
Running free, without a care
</Dialogues>
<SRT>
1
00:00:00,000 --> 00:00:05,000
Chasing sunsets on the horizon

2
00:00:05,000 --> 00:00:07,000
Feel the

3
00:00:07,000 --> 00:00:10,000
wind in my hair

4
00:00:10,000 --> 00:00:15,000
Running freely, without care
</SRT>

<Result>
<Matching>
1
00:00:00,000 --> 00:00:05,000
Chasing sunsets on the horizon
Match: "Chasing sunsets, on the horizon" matches with SRT "Chasing sunsets on the horizon".

2
00:00:05,000 --> 00:00:10,000
Feel the
Partial match: "Feel the breeze, in my hair" is similar to SRT "Feel the wind in my hair".

3
00:00:07,000 --> 00:00:10,000
wind in my hair
Partial match: "Feel the breeze, in my hair" is similar to SRT "Feel the wind in my hair".

4
00:00:11,000 --> 00:00:15,000
Running freely, without care
Match: "Running free, without a care" closely matches SRT "Running freely, without care".
</Matching>
<Summary>
1
00:00:00,000 --> 00:00:05,000
Chasing sunsets, on the horizon

2
00:00:05,000 --> 00:00:10,000
Feel the breeze, in my hair

3
00:00:10,000 --> 00:00:15,000
Running free, without a care
</Summary>
</Result>
</Example>

` + "<Dialogues>\n" + lyrics.Plain + "\n</Dialogues>\n<SRT>\n" + lyrics.TranscriptionData.Transcription + "\n</SRT>\n\n```xml\n<Result>"},
	}

	option := ComplectionOption{
		Model:     llmModel,
		MaxTokens: &maxTokens,
		StopWords: []string{"</Summary>"},
	}

	option.SetTemperature(temperature)

	response, err := chatAI.TextComplete(ctx, messages, option)
	if err != nil {
		return "", err
	}

	return response, nil
}
