import os
from dotenv import load_dotenv
import anthropic

class ClaudeClient:
    _instance = None
    _client = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if self._client is not None:
            return
            
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def client(self):
        return self._client 