# RAG

## Installation

We use [Poetry](https://python-poetry.org/) to manage dependencies.

```bash
poetry shell
poetry install
```


Create `testdata` directory in the root directory and add files.

> Now we only support `.md`, `.txt`, `.docx`, `.pdf` files.

> You can also import documents from github repositories.

Use pre-commit.
```bash
pre-commit install
```


 Create a `.env` file in the root directory and add the following environment variables:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<LANGCHAIN_API_KEY>
MODEL_API=<the model api from Mattermost>
ACCESS_TOKEN=<Github access token>
```
> Note:
> 1. You can get the `LANGCHAIN_API_KEY` from [LangSmith](https://www.langchain.com/langsmith).
> 2. Get the `MODEL_API` from [Mattermost](https://chat.coscup.org/coscup/pl/hjez3dwmtjbk8du1rih9ne66wo).
> 3. How to get Github access token: [Github Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).


## Usage

### Qdrant

Default port:6333
> If you want to change the port, please modify the `addData/docker-compose.yml` and `config.yaml`.

### Add or Update Data
如果要新增或修改資料請使用此方法
```bash
cd vectorDB
docker-compose -f addData/docker-compose.yml up -d  
```
### Run DB
```bash
cd vectorDB
docker build -t polyhistor:db .
docker run -d --restart always -p 6333:6333 --name polyhistor_qdrant polyhistor:db
```

### Create Qdrant collection
```bash
cd vectorDB
python3 create_collection.py
```

### Import documents to vectorDB
```bash
cd vectorDB
python3 read_docs.py
```

### Ollama

Run Ollama:
```bash
ollama serve
```
> Default embedding model is `chevalblanc/acge_text_embedding` and default language model is `ycchen/breeze-7b-instruct-v1_0`.

### Backend
```bash
poetry run uvicorn index:app --reload --host 0.0.0.0 --port 8000
```

Now you can access the API at `http://localhost:8000/api/v1/ask`.

### Q & A

Open a new terminal and run the following command:
```bash
cd src
python main.py
```

Then you can ask questions to the model.
If you want to exit, type `bye`.
