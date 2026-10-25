import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


def create_gemini_model() -> ChatGoogleGenerativeAI:
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
        max_retries=2,
    )
