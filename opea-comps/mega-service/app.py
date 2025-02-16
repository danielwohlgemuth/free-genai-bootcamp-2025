# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import json
import os
from fastapi import Request
from comps import MicroService, ServiceOrchestrator, ServiceRoleType, ServiceType
from comps.cores.proto.docarray import LLMParams

MEGA_SERVICE_PORT = int(os.getenv("MEGA_SERVICE_PORT", 8888))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


class VocabImporterService:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.megaservice = ServiceOrchestrator()
        self.endpoint = "/"

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

    async def handle_request(self, request: Request):
        data = await request.json()
        topic = data.get("topic")
        word_count = data.get("word_count", 5)
        
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

        result_dict, runtime_graph = await self.megaservice.schedule(
            initial_inputs={ "prompt": prompt },
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
            return vocab_data
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
    vocab_importer = VocabImporterService(port=MEGA_SERVICE_PORT)
    vocab_importer.start()