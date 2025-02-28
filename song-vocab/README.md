# Song Vocab

## vLLM
I tried to use vLLM but ran into issues trying to make it work.
There are no pre-built solutions to run on macOS, so it needs to be compiled from scratch. I first tried to build the Docker image, but that failed due to a missing dependency. Then I tried build from source, which succeeded, but when I tried to invoke the model, it was only generating exclamation marks. See a [similar issue](https://github.com/vllm-project/vllm/issues/13035).
I tried downgrading to v0.6.6, but then I couldn't even compile the code because the dependency installation failed with `ERROR: No matching distribution found for torch==2.5.0+cpu`.
I decided to use Ollama again as that has a Docker image and just works.

## LangChain vs LlamaIndex
After skimming through the [LangChain](https://python.langchain.com/docs/introduction/) and [LlamaIndex](https://docs.llamaindex.ai/en/stable/) documentation and reading comparisons between the two LLM frameworks, LlamaIndex seemed more useful when connecting with databases and LangChain seemed more useful when building agents.
Both could be used to build this project, but I decided to go with LangChain because it has a more extensive documentation with many examples.

