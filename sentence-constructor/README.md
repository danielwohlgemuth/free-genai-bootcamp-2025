# Sentence Constructor Comparison

## Evaluated chatbots:

- [ChatGPT](/sentence-constructor/chatgpt/README.md)
- [DeepSeek](/sentence-constructor/deepseek/README.md)

## Hypothesis and Technical Uncertainty

I assume that the free tier of ChatGPT and DeepSeek is enough to build a language translation assistant. I expect the chatbots will closely follow the instructions that were given to them.

## Technical Exploration

I used ChatGPT GPT-4 (Free, Temporary Chat) and DeepSeek V3 (Free) to build the translation assistant. Both were usable but had the tendency to provide the complete translation when the student was getting close to translating it correctly, so different attempts were made to suppress that behavior, including instructing to use example sentences that are different from the one the student provided, include good and bad examples in the instructions, and use other chatbots like Claude and Gemini to reword the instructions.

## Final Outcomes

Both ChatGPT and DeepSeek were useful as translation assistants at the free-tier level. Both had the tendency to reveal the complete translation when the student was close to getting it right. Instructions to prevent that were not being followed completely. Guardrails might help enforce the correct behavior. The output tended to be very verbose, so additional instructions should be included to make the response more concise.
Describe your final outcomes or domain knowledge acquired.
