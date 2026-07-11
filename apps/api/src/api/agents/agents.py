
from google import genai
from groq import Groq
from openai import OpenAI
from api.core.config import config


def run_llm(provider: str, model_name: str, messages: list[dict], max_tokens: int = 500):
    if provider == "openai":
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    elif provider == "groq":
        client = Groq(api_key=config.GROQ_API_KEY)
    else:
        client = genai.Client(api_key=config.GOOGLE_API_KEY)

    if provider == "google":
        return client.models.generate_content(
            model=model_name,
            contents=[message["content"] for message in messages],
        ).text

    if provider == "openai":
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            reasoning_effort="minimal",
            max_completion_tokens=max_tokens,
        ).choices[0].message.content

    return client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=max_tokens,
    ).choices[0].message.content