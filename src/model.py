import os
from typing import Any, Literal, Mapping

import requests
from dotenv import load_dotenv
from langchain.llms.base import LLM
from pydantic import Extra

load_dotenv()


class llm_model(LLM):
    model: Literal["llama2", "gemma", "ycchen/breeze-7b-instruct-v1_0", "mistral"]
    llm_url = os.getenv("MODEL_API")

    def __init__(self, model: str):
        super().__init__(model=model)

    class Config:
        extra = Extra.forbid

    @property
    def _llm_model_category(self) -> str:
        return self.model

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"llmUrl": self.llm_url}

    def __call__(self, prompt: str):
        return self._call(prompt)

    def _call(self, prompt: str, stop=None) -> str:
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}

        headers = {"Content-Type": "application/json"}

        response = requests.post(self.llm_url, json=payload, headers=headers, verify=False)
        response.raise_for_status()

        response = response.json()
        return response["choices"][0]["message"]["content"]  # get the response from the API
