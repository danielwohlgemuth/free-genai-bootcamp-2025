# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import json
import os
import requests
from typing import Dict, List
from fastapi import Body
from comps import MicroService, ServiceOrchestrator, ServiceRoleType, ServiceType
from comps.cores.proto.docarray import LLMParams
from pydantic import BaseModel

MEGA_SERVICE_PORT = int(os.getenv("MEGA_SERVICE_PORT", 8888))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


class VocabGeneratorRequest(BaseModel):
    topic: str
    word_count: int

class VocabGeneratorPartsResponse(BaseModel):
    type: str
    formality: str

class VocabGeneratorWordsResponse(BaseModel):
    japanese: str
    romaji: str
    english: str
    parts: VocabGeneratorPartsResponse

class VocabGeneratorResponse(BaseModel):
    group_name: str
    words: List[VocabGeneratorWordsResponse]

class VocabGeneratorService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.megaservice = ServiceOrchestrator()
        self.endpoint = "/v1/vocab_generator"

    def add_remote_service(self):
        llm = MicroService(
            name="llm",
            host=OLLAMA_HOST,
            port=OLLAMA_PORT,
            endpoint="/api/generate",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )
        self.megaservice.add(llm)

    async def handle_request(self, request: VocabGeneratorRequest = Body(...)) -> VocabGeneratorResponse:
        topic = request.topic
        word_count = request.word_count
        
        if not topic or not isinstance(word_count, int) or word_count < 3 or word_count > 10:
            raise ValueError("Invalid input: topic required and word_count must be between 3-10")

        prompt = f"""Generate exactly {word_count} Japanese vocabulary words related to the topic '{topic}'.
For each word, provide:
- The Japanese word (either kanji or kana)
- Romaji (romanized form)
- English translation
- Part of speech
- Formality level (casual/formal/polite)

Format the response as a JSON object exactly matching this structure:
{{ "group_name": "{topic}", "words": [{{ "japanese": "...", "romaji": "...", "english": "...", "parts": {{ "type": "...", "formality": "..." }} }} ] }}

Example:
{{ "group_name": "Basic Greetings", "words": [{{ "japanese": "こんにちは", "romaji": "konnichiwa", "english": "hello", "parts": {{ "type": "greeting", "formality": "neutral" }} }} ] }}

Only respond with the valid JSON object, nothing else."""

        parameters = LLMParams(
            model=OLLAMA_MODEL,
            max_tokens=2048,
            temperature=0.7,
            stream=False,
        )

        format = {
            "type": "object",
            "properties": {
                "group_name": {
                    "type": "string"
                },
                "words": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "japanese": {
                                "type": "string"
                            },
                            "romaji": {
                                "type": "string"
                            },
                            "english": {
                                "type": "string"
                            },
                            "parts": {
                                "type": "object",
                                "properties": { 
                                    "type": {
                                        "type": "string"
                                    },
                                    "formality": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": [
                "group_name",
                "words"
            ]
        }

        result_dict, runtime_graph = await self.megaservice.schedule(
            initial_inputs={
                "prompt": prompt,
                "format": format
            },
            llm_parameters=parameters,
        )

        last_node = runtime_graph.all_leaves()[-1]
        print('===============================================')
        print('result_dict', result_dict)
        print('===============================================')
        print('result_dict[last_node]["response"]', result_dict.get(last_node, {}).get("response", "{}"))
        print('===============================================')
        response = result_dict.get(last_node, {}).get("response", "{}")
        
        # Parse the response to ensure it matches the expected format
        try:
            vocab_data = json.loads(response)
            return VocabGeneratorResponse(**vocab_data)
        except json.JSONDecodeError:
            raise ValueError("Failed to generate properly formatted vocabulary data")

    def start(self):
        self.service = MicroService(
            self.__class__.__name__,
            service_role=ServiceRoleType.MEGASERVICE,
            host=self.host,
            port=self.port,
            endpoint=self.endpoint,
        )

        self.service.add_route(self.endpoint, self.handle_request, methods=["POST"])
        self.add_remote_service()
        self.service.start()


if __name__ == "__main__":
    # Make sure the model is loaded
    requests.post(f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/pull", data=f'{{"model": "{OLLAMA_MODEL}"}}')
    
    vocab_importer = VocabGeneratorService(port=MEGA_SERVICE_PORT)
    vocab_importer.start()