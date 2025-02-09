# Architectural Design

### Conceptual Architecture Diagram

![conceptual architecture diagram](/genai-architecting/conceptual-architecture-diagram.drawio.png)

[Conceptual Architecture Diagram file](https://app.diagrams.net/?title=conceptual-architecture-diagram#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fdanielwohlgemuth%2Ffree-genai-bootcamp-2025%2Frefs%2Fheads%2Fmain%2Fgenai-architecting%2Fconceptual-architecture-diagram.drawio)

### Sentence Constructor

![sentence constructor](/genai-architecting/sentence-constructor.drawio.png)

[Sentence Constructor file](https://app.diagrams.net/?title=sentence-constructor#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fdanielwohlgemuth%2Ffree-genai-bootcamp-2025%2Frefs%2Fheads%2Fmain%2Fgenai-architecting%2Fsentence-constructor.drawio)

## Requirements

This project is about a Japanese language learning portal (Lang Portal) using GenAI to support the learning experience.
GenAI (short for Generative Artificial Intelligence) allows creating content like giving answers to questions (ChatGPT, Google Gemini), creating images from text descriptions (DALL-E, Midjourney), or writing code based on written specifications (GitHub Copilot, Codeium).

The learning portal will offer study activities to help learning the Japanese language in different ways.
Some of the study activities that are planned to be supported are:
- Writing Practicing App
- Text Adventure Immersion Game
- Light Visual Novel Immersion Reading
- Sentence Constructor
- Visual Flashcard Vocab
- Speak to Learn

## Risks

The GenAI models that will be used are trained on a large amount of data and are capable of handling different topics. The language portal could be abused to generate content unrelated to learning Japanese. To limit this, input and output guardrails will be added to the system.

## Constraints

Since students are often cash constrained, the project will make use of smaller models to keep the costs down.
In addition and where possible, requests will be cached to reduce the number of expensive requests being processed.

## Model Selection and Development

Only models that have been trained with Japanese content will be considered and because of cost constraints, a large language model (LLM) with 7 billion parameters (7B) will be preferred over a LLM with 70 billion parameters (70B) if the accuracy of the smaller model is acceptable.

## Infrastructure Design

The project will run on AWS and make use of cloud native services to be able to scale automatically based on the demand.
