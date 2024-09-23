package main

import (
	"context"
	"log"
)

func syncPipeline(ctx context.Context, lyrics *LyricsData) (string, error) {
	chatAI, err := NewOpenAIClient()
	// llmModel := "claude-3-5-sonnet-20240620"
	// maxTokens := 8192
	llmModel := "gpt-4o-2024-08-06"
	maxTokens := 8192
	temperature := float32(0.75)

	if err != nil {
		log.Println(err)
	}

	messages := []Message{
		&UserMessage{`**Instructions**:

1. **Read through the Dialogues and the SRT file**: Understand the flow and structure of both documents.

2. **Identify Key Phrases**: For each line in the dialogues, pick out key phrases or unique words that will help you match the dialogues to the SRT content.

3. **Match the Dialogues to the SRT Content**: Begin with the first line of the SRT file and try to match it with the dialogues using the key phrases you've identified. Should through every line of SRT. and also must avoid to skip the SRT lines in this process.

4. **Document Each Match**: When you find a match, note the sequence number, timing from the SRT file, and both versions of the dialogues for comparison.

5. **Summarize Your Findings**: After going through all the dialogues and SRT content, summarize the SRT timings and its dialogues for all matched lines. Ensure summary should follow SRT format.

**Dialogues Example**:
<Dialogues>
Chasing sunsets, on the horizon
Feel the breeze, in my hair
Running free, without a care
</Dialogues>

**SRT Example**:
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

**Result Example**:
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
`},
		&AssistatntMessage{"Thank you for the instructions and examples. Please provide me with the dialogues and the SRT file so that I can begin the matching process as outlined."},
		&UserMessage{"<Dialogues>" + lyrics.Plain + "</Dialogues><SRT>" + lyrics.TranscriptionData.Transcription + "</SRT>"},
		&AssistatntMessage{`Thank you for providing the dialogues and SRT file. I will follow the instructions to match the dialogues with the SRT content and provide a summary.

<Result>
<Matching>`},
	}

	option := ComplectionOption{
		Model:     llmModel,
		StopWords: []string{"</Summary>"},
		MaxTokens: &maxTokens,
	}

	option.SetTemperature(temperature)

	response, err := chatAI.TextComplete(ctx, messages, option)
	if err != nil {
		return "", err
	}

	return response, nil
}
