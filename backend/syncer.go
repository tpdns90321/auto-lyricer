package main

import (
	"context"
	"fmt"
	"log"

	"github.com/liushuangls/go-anthropic"
)

func syncPipeline(ctx context.Context, anthrophic *AnthropicClient, lyrics *LyricsData) (string, error) {
  messages := []Message{
    &UserMessage{`**Instructions**:

1. **Read through the Dialogues and the SRT File**: Understand the flow and structure of both documents.

2. **Identify Key Phrases**: For each line in the dialogues, pick out key phrases or unique words that will help you match the dialogues to the SRT content.

3. **Match the Dialogues to the SRT Content**: Begin with the first line of the SRT file and try to match it with the dialogues using the key phrases you've identified.

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
00:00:05,000 --> 00:00:10,000
Feel the wind in my hair

3
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
Feel the wind in my hair
Partial match: "Feel the breeze, in my hair" is similar to SRT "Feel the wind in my hair".

3
00:00:12,000 --> 00:00:17,000
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
00:00:12,000 --> 00:00:17,000
Running free, without a care
</Summary>
</Result>
`},
    &AssistatntMessage{"Thank you for the instructions and examples. Please provide me with the dialogues and the SRT file so that I can begin the matching process as outlined."},
    &UserMessage{fmt.Sprintf("<Dialogues>%s</Dialogues><SRT>%s</SRT>",lyrics.Plain, lyrics.VideoData.Transcription)},
  }
  log.Println(messages)

  option := ComplectionOption{
    Model: anthropic.ModelClaude3Sonnet20240229,
    MaxTokens: 4096,
  }

  option.SetTemperature(0.05)

  response, err := anthrophic.TextComplete(ctx, messages, option)
  if err != nil {
    return "", err
  }

  return response, nil
}
