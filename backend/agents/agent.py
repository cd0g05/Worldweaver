import logging
import os
from abc import ABCMeta, abstractmethod
from typing import Optional

from anthropic import Anthropic, APIStatusError, APIConnectionError

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    vertexai = None
    GenerativeModel = None
    VERTEX_AI_AVAILABLE = False

# from src.media_lens.common import LOGGER_NAME, AI_PROVIDER, ANTHROPIC_MODEL, VERTEX_AI_PROJECT_ID, VERTEX_AI_LOCATION, VERTEX_AI_MODEL

logger = logging.getLogger("Hi")

class Agent(metaclass=ABCMeta):
    """
    Base class for all agents.
    """
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    @abstractmethod
    def invoke(self, user_prompt: str) -> str:
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

    @classmethod
    def get_agent(cls, agent_type: str, prompt_name: str) -> "Agent":
        if agent_type == "vertex":
            prompt = "Talk like a pirate"
            agent: Agent = GoogleVertexAIAgent(prompt)
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
    def __init__(self, system_prompt: str, project_id: str, location: str, model: str):
        super().__init__(system_prompt)
        if not VERTEX_AI_AVAILABLE:
            raise ImportError("google-cloud-aiplatform package is required for Google Vertex AI support")

        vertexai.init(project=project_id, location=location)
        self.client = GenerativeModel(model)
        self._model = model

    def invoke(self, user_prompt: str) -> str:
        try:
            # Combine system and user prompts for Vertex AI

            # TODO   change this to use placeholder vs concatenating
            full_prompt = f"{self.system_prompt}\n\n{user_prompt}"

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

