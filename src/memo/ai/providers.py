"""AI model providers for Memo."""

import os
from abc import ABC, abstractmethod
from typing import Optional

import click
import google.generativeai as genai
from openai import OpenAI

from ..config.environment import load_environment_variables

# Load environment variables from all sources
load_environment_variables()


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate_message(self, prompt: str) -> Optional[str]:
        """Generate a commit message using the AI provider."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI provider is available (API key configured)."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""

    def __init__(self, model: str = "gpt-4.1-mini"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_message(self, prompt: str) -> Optional[str]:
        """Generate a commit message using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates conventional commit messages.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            click.echo(f"Error generating commit message with OpenAI: {e}")
            return None

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return os.getenv("OPENAI_API_KEY") is not None


class GeminiProvider(AIProvider):
    """Google Gemini provider."""

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def generate_message(self, prompt: str) -> Optional[str]:
        """Generate a commit message using Gemini."""
        if not self.api_key:
            click.echo("Error: GOOGLE_API_KEY environment variable not set.")
            return None

        try:
            gemini_model = genai.GenerativeModel(self.model)
            response = gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            click.echo(f"Error generating commit message with Gemini: {e}")
            return None

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return self.api_key is not None


def get_ai_provider(model: str) -> Optional[AIProvider]:
    """Factory function to get the appropriate AI provider."""
    if model == "gpt-4.1-mini":
        return OpenAIProvider(model)
    elif model in ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"]:
        return GeminiProvider(model)
    else:
        click.echo(f"Error: Unsupported model '{model}'.")
        return None
