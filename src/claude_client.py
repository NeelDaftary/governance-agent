import os
import logging
from dotenv import load_dotenv
import anthropic

# Configure logging
logger = logging.getLogger(__name__)

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
            
        try:
            load_dotenv()
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                logger.error("ANTHROPIC_API_KEY not found in environment variables")
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
            logger.info("Initializing Anthropic client")
            self._client = anthropic.Anthropic(api_key=api_key)
            logger.info("Successfully initialized Anthropic client")
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {str(e)}")
            raise

    @property
    def client(self):
        if self._client is None:
            logger.error("Anthropic client not initialized")
            raise ValueError("Anthropic client not initialized")
        return self._client 