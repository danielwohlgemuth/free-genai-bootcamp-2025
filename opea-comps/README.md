# OPEA Comps

![opea comps architecture](/opea-comps/assets/opea-comps-architecture.drawio.png)

[OPEA Comps Architecture file](https://app.diagrams.net/?title=opea-comps-architecture#Uhttps%3A%2F%2Fraw.githubusercontent.com%2Fdanielwohlgemuth%2Ffree-genai-bootcamp-2025%2Frefs%2Fheads%2Fmain%2Fopea-comps%2Fassets%2Fopea-comps-architecture.drawio)

Note that the result of the Vocabulary Generator can be used to add a new JSON file in the [lang-portal/backend_python/db/seeds](/lang-portal/backend_python/db/seeds) folder.

## Results

- ~~The `llama3.2:1b` model was able to generate a valid JSON response in most cases, but it would sometimes fail to include the last `}` in the response, making the JSON parser fail. An additional step would be needed that gets the response into a good shape or asks the model to fix it if it's not a valid response.~~

- ~~The `deepseek-r1:1.5b` model wasn't able to generate a valid JSON response because it also included it's thinking process in the response. A special cleanup step would be needed to return only the JSON response.~~

- Both issues were fixed by specifying the JSON response format in the prompt. Both `llama3.2:1b` and `deepseek-r1:1.5b` were able to generate a valid JSON response.

- Error handling needs to be improved. There is some kind of telemetry collector issue (`requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=4318) ...`, port 4318 is an Open Telemetry port) that is filling up the logs with distracting information when there is an error.

## [Ollama](./llm/README.md)

## [Mega Service](./mega-service/README.md)

## [Vocabulary Generator](./vocab_generator/README.md)
