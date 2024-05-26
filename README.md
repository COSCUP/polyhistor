# RAG

## Installation

We use [Poetry](https://python-poetry.org/) to manage dependencies.

```bash
poetry shell
poetry install
```


Create `testdata` directory in the root directory and add files.

> Now we only support `.md` files.

Use pre-commit.
```bash
pre-commit install
```


(Optional) Create a `.env` file in the root directory and add the following environment variables:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<LANGCHAIN_API_KEY>
MODEL_API=<the model api from Mattermost>
```
> Note:
> 1. You can get the `LANGCHAIN_API_KEY` from [LangSmith](https://www.langchain.com/langsmith).
> 2. Get the `MODEL_API` from [Mattermost](https://chat.coscup.org/coscup/pl/hjez3dwmtjbk8du1rih9ne66wo).


## Usage

Run ollama:
```bash
ollama serve
```
> Default embedding model is `chevalblanc/acge_text_embedding` and default language model is `qwen:4b`.

Open a new terminal and run the following command:
```bash
cd src
python main.py
```

Then you can ask questions to the model.
If you want to exit, type `bye`.
