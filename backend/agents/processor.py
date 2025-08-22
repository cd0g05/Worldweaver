from pyexpat import model

from backend.agents.agent import Agent
from backend.agents.agent_map import AgentMap
from pathlib import Path
import toml

class Processor:

    def __init__(self, model: str):
        self.model = model
        self.agent_map = AgentMap()

    def get_llm_response(self, stage:int, user_prompt:str, chat_context:str, document_context:str):
        try:
            prompt_name: str = self.agent_map.get_prompt(stage)
        except KeyError as e:
            return f"Invalid stage: {e}"
        model: str = "gemini"
        agent: Agent = Agent.get_agent(model, prompt_name, 1)
        return agent.invoke(user_prompt, chat_context, document_context)

    def get_tutorial_response(self, stage:int, chat_context:str, document_context:str):
        stage_list = self.get_toml_contents("tutorial_list:2", Path("/Users/cartercripe/dev/code/projects/worldweaver/backend/config/prompts"))
        unformatted_prompt = self.get_toml_contents("tutorial_prompt:1", Path("/Users/cartercripe/dev/code/projects/worldweaver/backend/config/prompts"))
        stage_title = self.get_stage_title(stage)
        formatted_prompt = unformatted_prompt.format(stages_list=stage_list, stage_title=stage_title, doc="{doc}", chat="{chat}")
        agent: Agent = Agent.get_agent(self.model, formatted_prompt, 0)

        return agent.invoke("", chat_context, document_context)

    def get_toml_contents(self, file_name: str, file_dir_path: Path) -> str:
        if not file_dir_path.is_dir():
            raise NotADirectoryError(f"Prompt directory not found: {file_dir_path}")

        fname, vers = file_name.split(":")
        with open(str(file_dir_path / f"{fname}.toml"), 'r') as file:
            toml_content = toml.load(file)

        if vers == "latest":
            versions = [key for key in toml_content.keys() if key.startswith('v')]
            version = max(versions, key=lambda v: int(v[1:]))
        else:
            version = f"v{vers}"
        return toml_content[version]

    def get_stage_title(self, num: int) -> str:
        names = {
            # Section 1: Getting Started
            1: "Stage 1: Your Big Idea",
            2: "Stage 2: Working Title",
            3: "Stage 3: Genre & Flavor",
            4: "Stage 4: Main Vibe",
            5: "Stage 5: One-Sentence Pitch",

            # Section 2: Worldbuilding Basics
            6: "Stage 6: Setting",
            7: "Stage 7: Time Period",
            8: "Stage 8: The Map",
            9: "Stage 9: The Environment",
            10: "Stage 10: Magic: Yes or No",

            # Section 3: Worldbuilding Expanded
            11: "Stage 11: Magic Rules",
            12: "Stage 12: History Snapshot",
            13: "Stage 13: Groups & Cultures",
            14: "Stage 14: Government & Power",
            15: "Stage 15: Everyday Life",
            16: "Stage 16: Creatures",
            17: "Stage 17: Plants & Resources",

            # Section 4: Characters
            18: "Stage 18: Your Hero",
            19: "Stage 19: What They Want",
            20: "Stage 20: What’s in Their Way",
            21: "Stage 21: Your Villain",
            22: "Stage 22: Why They Oppose",
            23: "Stage 23: Sidekick or Ally",
            24: "Stage 24: Other Important Characters",
            25: "Stage 25: Character Secrets",

            # Section 5: Plot Basics
            26: "Stage 26: Choose a Story Shape",
            27: "Stage 27: Inciting Incident",
            28: "Stage 28: Turning Point #1",
            29: "Stage 29: Midpoint Twist",
            30: "Stage 30: Turning Point #2",
            31: "Stage 31: Climax",
            32: "Stage 32: Resolution",

            # Section 6: Plot Expanded
            33: "Stage 33: Stakes",
            34: "Stage 34: Theme (Optional)",
            35: "Stage 35: Subplots",
            36: "Stage 36: Foreshadowing",
            37: "Stage 37: Scene List",

            # Section 7: Writing Style
            38: "Stage 38: Point of View",
            39: "Stage 39: Tone",
            40: "Stage 40: Audience",
            41: "Stage 41: Length Goal",
            42: "Stage 42: Sample Paragraph"
        }
        return names.get(num, "Invalid stage number")

