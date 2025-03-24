package main

import "context"

type Message interface {
	Content() *string
}

type AssistatntMessage struct {
	string
}

func (m *AssistatntMessage) Content() *string {
	return &m.string
}

type UserMessage struct {
	string
}

func (m *UserMessage) Content() *string {
	return &m.string
}

type ComplectionOption struct {
	Model        string
	SystemPrompt string
	StopWords    []string
	MaxTokens    *int
	Temperature  *float32
	TopP         *float32
	TopK         *int
}

// ComplectionOption's Setters
func (o *ComplectionOption) SetSystemPrompt(prompt string) {
	o.SystemPrompt = prompt
}

func (o *ComplectionOption) SetStopWords(words []string) {
	o.StopWords = words
}

func (o *ComplectionOption) SetMaxTokens(tokens int) {
	o.MaxTokens = &tokens
}

func (o *ComplectionOption) SetTemperature(temperature float32) {
	o.Temperature = &temperature
}

func (o *ComplectionOption) SetTopP(topP float32) {
	o.TopP = &topP
}

func (o *ComplectionOption) SetTopK(topK int) {
	o.TopK = &topK
}

type TextComplection interface {
	TextComplete(ctx context.Context, messages []Message, option ComplectionOption) (string, error)
}
