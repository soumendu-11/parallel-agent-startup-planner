"""Centralized LLM configuration — all nodes share this."""

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()


def get_llm(temperature: float = 0.4) -> AzureChatOpenAI:
    """Return an Azure OpenAI LLM instance configured from .env."""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("AZURE_API_KEY"),
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        api_version=os.getenv("API_VERSION"),
        temperature=temperature,
    )
