package main

import (
	"context"
	"log"
)

func syncPipeline(ctx context.Context, lyrics *LyricsData) (string, error) {
	// claude-3-5-{sonnet,haiku}-20241022
	chatAI, err := NewAnthrophicClient()
	llmModel := "claude-3-5-sonnet-20241022"
	//llmModel := "claude-3-5-haiku-20241022"
	maxTokens := 8192
	temperature := float32(0.0)

	// openai GPT-4o{,-mini}
	//chatAI, err := NewOpenAIClient()
	//llmModel := "gpt-4o-2024-08-06"
	//llmModel := "gpt-4o-mini-2024-07-18"
	//maxTokens := 16384
	//temperature := float32(.8)

	// gemini
	//chatAI, err := NewGeminiClient()
	//chatAI, err := NewGeminiOpenaiClient()
	//llmModel := "gemini-1.5-pro-002"
	//llmModel := "gemini-1.5-flash-002"
	//maxTokens := 8192
	//temperature := float32(.6)

	// xai
	//chatAI, err := NewXaiClient()
	//llmModel := "grok-beta"
	//maxTokens := 8192
	//temperature := float32(0.4)

	if err != nil {
		log.Println(err)
	}

	messages := []Message{
		&UserMessage{`Repeat dialogues through by each sequence with its latin pronunciation.
Also repeat SRT through by each sequence with matching between each sequence's pronunciation without translation and similar line of dialogue's pronunciation.
After repeating SRT, you will generate new SRT with replaced dialogues.
Any repetition and new SRT should be without omission of parts.

YOU SHOULD ITERATE EVERY PARTS OF DIALOGUES AND MATCHING, NEW SRT WITHOUT OMISSION.

<Example>
<Dialogues>
Chasing sunsets, on the horizon
Feel the breeze, in my hair
Running free, without a care
</Dialogues>
<SRT>
1
00:00:01,000 --> 00:00:05,000
Chasing sunsets on the horizon

2
00:00:05,000 --> 00:00:07,000
Feel the

3
00:00:07,000 --> 00:00:10,000
wind in my hair

4
00:00:10,000 --> 00:00:15,000
Ah freely without

5
00:00:15,000 --> 00:00:16,000
Ah

</SRT>

<Steps>
<Dialogues>
(CHAYsing SUNsets, on the huhRYEzun)Chasing sunsets, on the horizon
(FEEL thuh BREEZ, in my HAIR)Feel the breeze, in my hair
(RUNing FREE, wihTHOWT uh KAIR)Running free, without a care
</Dialogues>
<Matching>
1
00:00:01,000 --> 00:00:05,000
Chasing sunsets on the horizon(CHAYsing SUNsets, on the huhRYEzun) and (CHAYsing SUNsets, on the huhRYEzun)"Chasing sunsets, on the horizon" are matched.

2
00:00:05,000 --> 00:00:07,000
Feel the(FEEL thuh) and (FEEL thuh BREEZ, in my HAIR)"Feel the breeze, in my hair" are partial matched.

3
00:00:07,000 --> 00:00:10,000
wind in my hair(WIND in my HAIR) and (FEEL thuh BREEZ, in my HAIR)"Feel the breeze, in my hair" are partial matched.

4
00:00:10,000 --> 00:00:15,000
Ah freely without(ah FREElee wihTHOWT) and (RUNing FREE, wihTHOWT uh KAIR)"Running free, without a care" are partial matched.

5
00:00:15,000 --> 00:00:16,000
Ah(ah) does not match any Dialogues.

</Matching>
<NewSRT>
1
00:00:01,000 --> 00:00:05,000
Chasing sunsets, on the horizon

2
00:00:05,000 --> 00:00:10,000
Feel the breeze, in my hair

3
00:00:10,000 --> 00:00:15,000
Running free, without a care
</NewSRT>
</Steps>
</Example>

` + "<Dialogues>\n" + lyrics.Plain + "\n</Dialogues>\n<SRT>\n" + lyrics.TranscriptionData.Transcription + "\n</SRT>"},
		&AssistatntMessage{"```xml\n<Steps>"},
	}

	option := ComplectionOption{
		Model:     llmModel,
		MaxTokens: &maxTokens,
		StopWords: []string{"</NewSRT>"},
	}

	option.SetTemperature(temperature)

	response, err := chatAI.TextComplete(ctx, messages, option)
	if err != nil {
		return "", err
	}

	return response, nil
}
