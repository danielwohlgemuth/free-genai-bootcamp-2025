# Run Ollama using Docker Compose

This document includes instructions to run large language models on Ollama.

Initial instructions retrieved from
https://github.com/opea-project/GenAIComps/tree/main/comps/third_parties/ollama.

## Setup Ollama

Run Ollama using Docker Compose with the definition in [docker-compose.yaml](/opea-comps/docker-compose.yaml).

```bash
docker compose up -d
```

To interact with Ollama, review the API documentation at
https://github.com/ollama/ollama/blob/main/docs/api.md.

## Choose a model

Visit https://ollama.com/library to see the list of available models.

## List downloaded models

```bash
curl http://localhost:11434/api/tags
```

## Model evaluation

### Model [llama3.2:1b](https://ollama.com/library/llama3.2:1b)

Download model

```bash
docker exec ollama-server ollama run llama3.2:1b
```

or

```bash
curl http://localhost:11434/api/pull -d '{
  "model": "llama3.2:1b"
}'
```

#### Request

```bash
curl --noproxy "*" http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt":"Why is the sky blue?",
  "stream": false
}'
```

Response

```json
{
    "model": "llama3.2:1b",
    "created_at": "2025-02-16T13:01:39.303960419Z",
    "response": "The sky appears blue because of a phenomenon called Rayleigh scattering, named after the British physicist Lord Rayleigh, who first described it in the late 19th century. Here's a simplified explanation:\n\nWhen sunlight enters Earth's atmosphere, it encounters tiny molecules of gases such as nitrogen (N2) and oxygen (O2). These gas molecules are much smaller than the wavelength of light, which is why they scatter the light.\n\nLight with wavelengths longer than the size of the gas molecules (like red light) is not scattered as much, while light with wavelengths shorter than the size of the gas molecules (like blue light) is scattered more. This is because shorter wavelengths are more easily diffracted by the tiny molecules in the atmosphere.\n\nAs a result, the blue light is scattered in all directions, reaching our eyes from every part of the sky. Our brains then perceive the sky as blue due to the way we process this scattered light.\n\nIt's worth noting that during sunrise and sunset, the angle of the sunlight is such that it hits the atmosphere at an angle, which scatters the shorter wavelengths (like blue and violet) more than the longer wavelengths (like red and orange). This is why the sky can take on a reddish hue during these times.\n\nSo, to summarize, the sky appears blue because of the way light interacts with tiny molecules in the Earth's atmosphere, scattering shorter wavelengths like blue light and making the sky appear blue.",
    "done": true,
    "done_reason": "stop",
    "context": [...],
    "total_duration": 8419108670,
    "load_duration": 1585499334,
    "prompt_eval_count": 31,
    "prompt_eval_duration": 255000000,
    "eval_count": 292,
    "eval_duration": 6575000000
}
```

#### Request (Structured outputs)

```bash
curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d '{
  "model": "llama3.2:1b",
  "prompt": "Ollama is 22 years old and is busy saving the world. Respond using JSON",
  "stream": false,
  "format": {
    "type": "object",
    "properties": {
      "age": {
        "type": "integer"
      },
      "available": {
        "type": "boolean"
      }
    },
    "required": [
      "age",
      "available"
    ]
  }
}'
```

Response

```json
{
    "model": "llama3.2:1b",
    "created_at": "2025-02-16T14:08:47.292392631Z",
    "response": "{\n  \"age\": 22,\n  \"available\": true\n}",
    "done": true,
    "done_reason": "stop",
    "context": [...],
    "total_duration": 610349709,
    "load_duration": 24262792,
    "prompt_eval_count": 43,
    "prompt_eval_duration": 151000000,
    "eval_count": 20,
    "eval_duration": 433000000
}
```

#### Request (JSON mode)

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "What color is the sky at different times of the day? Respond using JSON",
  "format": "json",
  "stream": false
}'
```

Response

```json
{
    "model": "llama3.2:1b",
    "created_at": "2025-02-16T14:09:45.583037755Z",
    "response": "{\n  \"dawn\": \"#964B00\",\n  \"early_morning\": \"#E5EAEB\",\n  \"morning\": \"#C7D2BF\",\n  \"midday\": \"#808080\",\n  \"afternoon\": \"#6495ED\",\n  \"late afternoon\": \"#7A288A\",\n  \"evening\": \"#FFC499\",\n  \"twilight\": {\"color\": \"#FF9900\", \"time\": \"just before sunset\"}\n}",
    "done": true,
    "done_reason": "stop",
    "context": [...],
    "total_duration": 1866561167,
    "load_duration": 29972166,
    "prompt_eval_count": 40,
    "prompt_eval_duration": 138000000,
    "eval_count": 98,
    "eval_duration": 1696000000
}
```

#### Request (Chat)

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:1b",
  "messages": [
    {
      "role": "user",
      "content": "why is the sky blue?"
    }
  ],
  "stream": false
}'
```

Response

```json
{
    "model": "llama3.2:1b",
    "created_at": "2025-02-16T14:10:33.46305593Z",
    "message": {
        "role": "assistant",
        "content": "The sky appears blue to us because of a phenomenon called Rayleigh scattering, named after the British physicist Lord Rayleigh, who first described it in the late 19th century.\n\nHere's what happens:\n\n1. **Sunlight enters the Earth's atmosphere**: When the sun shines, its light travels through space and enters the Earth's atmosphere.\n2. **Light is scattered by atoms and molecules**: The shorter wavelengths of light, like blue and violet, are scattered more than the longer wavelengths, like red and orange. This is because these shorter wavelengths interact more strongly with the tiny molecules and atoms in the atmosphere.\n3. **Scattered light reaches our eyes**: As a result of this scattering, the blue light is dispersed throughout the atmosphere, while the other colors are not as much scattered or reach our eyes at all.\n4. **We see the blue sky**: Our brains then perceive these scattered blue wavelengths as the color blue, which we experience as the sky appears blue to us.\n\nThis effect is more pronounced during the daytime when the sun is overhead, and it's why the sky typically looks blue during this time. However, at sunrise and sunset, the light has to travel through more of the atmosphere, scattering off more particles and resulting in a redder hue.\n\nIt's worth noting that atmospheric conditions, such as pollution, dust, and water vapor, can also affect the color of the sky. But Rayleigh scattering is the primary reason why the sky appears blue."
    },
    "done_reason": "stop",
    "done": true,
    "total_duration": 6706118962,
    "load_duration": 25280458,
    "prompt_eval_count": 31,
    "prompt_eval_duration": 88000000,
    "eval_count": 297,
    "eval_duration": 6591000000
}
```

### Model [deepseek-r1:1.5b](https://ollama.com/library/deepseek-r1:1.5b)

Download model

```bash
docker exec ollama-server ollama run deepseek-r1:1.5b
```

#### Request

```bash
curl --noproxy "*" http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:1.5b",
  "prompt":"Why is the sky blue?",
  "stream": false
}'
```

Response

```json
{
    "model": "deepseek-r1:1.5b",
    "created_at": "2025-02-16T13:10:57.249310761Z",
    "response": "\u003cthink\u003e\n\n\u003c/think\u003e\n\nThe color of the sky, often referred to as a \"blue,\" is primarily due to the phenomenon called Rayleigh scattering. During the day when sunlight passes through Earth's atmosphere, it interacts with water molecules in the air and reflects this light in all directions. This scattered light gives the sky its blue color, especially during sunrise or sunset. The exact reason why the sky appears blue at these times is known as atmospheric transparency, a result of the short wavelength of visible light being scattered more efficiently than longer wavelengths (like blue) within the Earth's atmosphere.",
    "done": true,
    "done_reason": "stop",
    "context": [...],
    "total_duration": 3668448502,
    "load_duration": 1061640334,
    "prompt_eval_count": 9,
    "prompt_eval_duration": 129000000,
    "eval_count": 116,
    "eval_duration": 2476000000
}
```

## Cleanup

Unload model from memory

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "keep_alive": 0
}'

curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:1.5b",
  "keep_alive": 0
}'
```

Stop ollama container

```bash
docker compose down
```

Remove downloaded models

```bash
docker volume rm ollama_model_data
```
