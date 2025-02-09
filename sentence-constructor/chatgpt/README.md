# ChatGPT powered learning assistant

## Which model?

GPT-4 (Free, Temporary Chat)

## [Prompt](/sentence-constructor/chatgpt/prompt.md)

Final prompt.

## [Changelog](/sentence-constructor/chatgpt/changelog.md)

History of attempted prompts.

## Prompt engineering guide

https://platform.openai.com/docs/guides/prompt-engineering

https://cloud.google.com/vertex-ai/generative-ai/docs/chat/chat-prompts

- Give the chatbot an identity and persona.
- Give rules for the chatbot to follow.
- Add rules that prevent the exposure of context information.	
- Add a reminder to always remember and follow the instructions.	
- Test your chatbot and add rules to counteract undesirable behaviors.	
- Add a rule to reduce hallucinations.	
- Including prompt-response examples in the prompt helps the model learn how to respond.
- Give the model examples of the patterns to follow instead of examples of patterns to avoid.
- Include information (context) in the prompt that you want the model to use when generating a response.
- Give the model instructions on how to use the contextual information.
- Adding a partial answer to a prompt can guide the model to follow a desired pattern or format.
- Break down complex instructions into a prompt for each instruction and decide which prompt to apply based on the user's input.
- Break down multiple sequential steps into separate prompts and chain them such that the output on the preceding prompt becomes the input of the following prompt.
