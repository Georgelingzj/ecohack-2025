from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class BaseAgent(object):
    def __init__(
            self,
            model_name: str = "gpt-4o-mini",
            max_memory_records: int = 10
    ):
        self.model_name = model_name
        self.max_memory_records = max_memory_records

        self.client = OpenAI()
        self.async_client = AsyncOpenAI()

