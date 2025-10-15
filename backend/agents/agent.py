import logging
import json
import os
from google.oauth2 import service_account
from vertexai import init
from abc import ABCMeta, abstractmethod
import dotenv
from pathlib import Path
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python versions
from typing import Optional
from backend.utils.logging_config import get_module_logger
# from google.cloud import aiplatform

# from anthropic import Anthropic, APIStatusError, APIConnectionError

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    vertexai = None
    GenerativeModel = None
    VERTEX_AI_AVAILABLE = False

# from src.media_lens.common import LOGGER_NAME, AI_PROVIDER, ANTHROPIC_MODEL, VERTEX_AI_PROJECT_ID, VERTEX_AI_LOCATION, VERTEX_AI_MODEL

logger = get_module_logger('agent')

class Agent(metaclass=ABCMeta):
    """
    Base class for all agents.
    """
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    @abstractmethod
    def invoke(self, user_prompt: str, chat_context:str, doc_context:str) -> str:
        """
        Send the prompts to the LLM and return the response.
        :param user_prompt: specific user prompt
        :return: text of response
        """
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """
        Return the model name.
        :return: model name
        """
        pass

    @staticmethod
    def _load_system_prompt(prompt_ref: str, prompt_dir_path: Path) -> str:
        """
        Helper method to load and format the prompt. Assumes prompt_ref = "name:vers"
        """
        if not prompt_dir_path.is_dir():
            raise NotADirectoryError(f"Prompt directory not found: {prompt_dir_path}")

        fname, vers = prompt_ref.split(":")
        with open(str(prompt_dir_path / f"{fname}.toml"), 'rb') as file:
            toml_content = tomllib.load(file)

        if vers == "latest":
            versions = [key for key in toml_content.keys() if key.startswith('v')]
            version = max(versions, key=lambda v: int(v[1:]))
        else:
            version = f"v{vers}"
        return toml_content[version]

    @classmethod
    def get_agent(cls, agent_type: str, prompt_name: str, flag: int) -> "Agent":
        if agent_type == "anthropic":
            prompt = "Talk like a pirate"
            agent: Agent = GoogleVertexAIAgent(prompt_name, os.getenv("GOOGLE_CLOUD_PROJECT"), os.getenv("ANTHROPIC_SONNET_FOUR_LOCATION"), os.getenv("ANTRHOPIC_SONNET_FOUR_ID"), flag)
            return agent
        elif agent_type == "gemini":
            agent: Agent = GoogleVertexAIAgent(prompt_name, os.getenv("GOOGLE_CLOUD_PROJECT"), os.getenv("GEMINI_LOCATION"), os.getenv("GEMINI_PRO_2_5_ID"), flag)
            return agent

# class ClaudeLLMAgent(Agent):
#     """
#     Anthropic Claude LLM agent.
#     """
#     def __init__(self, api_key: str, model: str):
#         super().__init__()
#         self.client = Anthropic(api_key=api_key)
#         self._model = model
#
#     def invoke(self, system_prompt: str, user_prompt: str) -> str:
#         try:
#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=4096,
#                 temperature=0,
#                 system=system_prompt,
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": user_prompt
#                     }
#                 ]
#             )
#             logger.debug(f"Claude raw response: {response.content}")
#             if len(response.content) == 1:
#                 logger.debug(f".. response: {len(response.content[0].text)} bytes / {len(response.content[0].text.split())} words")
#                 return response.content[0].text
#             else:
#                 return "ERROR - NO DATA"
#         except (APIStatusError, APIConnectionError) as e:
#             logger.error(f"Claude API error: {str(e)}")
#             raise
#
#     @property
#     def model(self) -> str:
#         return self._model


class GoogleVertexAIAgent(Agent):
    """
    Google Vertex AI LLM agent.
    """
    def __init__(self, prompt_name: str, project_id: str, location: str, model: str, flag: int):
        if flag == 1:
            system_prompt = self._load_system_prompt(prompt_name, Path("backend/config/prompts"))
        else:
            system_prompt = prompt_name
        super().__init__(system_prompt)
        if not VERTEX_AI_AVAILABLE:
            raise ImportError("google-cloud-aiplatform package is required for Google Vertex AI support")
        logger.info("attempting to load Google Vertex AI")
        credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if credentials_json:
            logger.info("successfully loading Google Vertex AI credentials")
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            # Initialize Vertex AI with explicit credentials
            init(project=project_id, credentials=credentials, location=location)
        else:
            logger.warning("failed to load Google Vertex AI credentials")
        self.client = GenerativeModel(model)
        self._model = model

    def invoke(self, user_prompt: str, chat_context:str, doc_context:str) -> str:
        try:
            # Combine system and user prompts for Vertex AI

            # TODO   change this to use placeholder vs concatenating
            full_prompt = f"{self.system_prompt.format(chat=chat_context, doc=doc_context)}\n\n{user_prompt}"

            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 20000,  # Increased from 4096, still well under 64K limit
                }
            )

            logger.debug(f"Vertex AI raw response: {response.text}")
            logger.debug(f".. response: {len(response.text)} bytes / {len(response.text.split())} words")

            return response.text

        except Exception as e:
            logger.error(f"Vertex AI API error: {str(e)}")
            raise

    @property
    def model(self) -> str:
        return self._model

if __name__ == "__main__":
    dotenv.load_dotenv()
    agent:Agent = Agent.get_agent("gemini", "tutorial1:1")
    logger.info(agent.invoke("Who are you?"))