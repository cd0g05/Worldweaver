from dataclasses import replace
from sys import getallocatedblocks
from abc import ABCMeta, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from backend.agents.agent import Agent
import toml
load_dotenv()
import os
api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI()


class call_ai:
    def __init__(self):
        """Initialize the call_ai class"""
        pass

    def get_stub(self, content):
        if content == "insert":
            return {
                "type": "tool",
                "tool": "insert",
                "description": "Added Breaking Bad Quote",
                "index": 0,
                "text": "I am the one who knocks...",
                "style": "bold",
                "value": True,
                "source": "api"
            }
        elif content == "insert_end":
            return {
                "type": "tool",
                "tool": "insert",
                "description": "Added Breaking Bad Quote",
                "text": "I am the one who knocks...",
                "style": "bold",
                "value": True,
                "source": "api"
            }

        elif content == "llm_message":
            return {
                "type": "message",
                "text": "I am the one who knocks..."
            }
        elif content == "document_old":
            return {
                "type": "both",
                "text": "I have added a quote from the Lord of the Rings to the document, let me know if you want to change it.",
                "document": {
                    "tool": "insert",
                    "description": "Added LOTR Quote",
                    "index": 0,
                    "text": "All we have to decide is what to do with the time that is given to us."
                }
            }
        elif content == "document_new":
            return """<message>I have added a quote from the Lord of the Rings to the document, let me know if you want to change it.</message><document>{"tool": "insert", "description": "Added LOTR Quote", "index": 0, "text": "All we have to decide is what to do with the time that is given to us."}</document>"""
        elif content == "message_new":
            return "<message>I burn my life to make a sunrise I know I'll never see.</message>"
        elif content == "set":
            return {
            "type": "tool",
            "tool": "set",
            "text": (
                "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair."
            ),
            "source": "api"
        }

        # elif content == "get":
        #     return {
        #     "type": "tool",
        #     "tool": "get",
        #     "index": 0,
        #     "length": 29
        # }

        # elif content == "getall":
        #     return {
        #     "type": "tool",
        #     "tool": "getall",
        #     "index": 0
        # }

        elif content == "update":
            return {
            "type": "tool",
            "tool": "update",
            "index": 25,
            "length": 28,
            "text": " and the worst of times,",
            "source": "api"
        }

        elif content == "delete":
            return {
            "type": "tool",
            "tool": "delete",
            "index": 0,
            "length": 29,
            "source": "api"
        }

        elif content == "deleteall":
            return {
            "type": "tool",
            "tool": "deleteall",
            "source": "api"
        }

        elif content == "format":
            return {
            "type": "tool",
            "tool": "format",
            "index": 0,
            "length": 29,
            "formats": {
                "bold": True
            },
            "source": "api"
        }

        # elif content == "bounds":
        #     return {
        #     "type": "tool",
        #     "tool": "bounds",
        #     "index": 0,
        #     "length": 29
        # }
        else:
            return "failed"

    def get_response(self, prompt, content):
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": content}
            ]
        )
        return response.choices[0].message.content

    def tools(self):
        tools_list = {
            "insertText(index: number, text: string, format: string, value: any, source: string = 'api'): Delta"
            "getContents(index: number = 0, length: number = remaining): Delta"
            "updateContents(delta: Delta, source: string = 'api'): Delta"
            "deleteText(index: number, length: number, source: string = 'api'): Delta"
            "formatText(index: number, length: number, formats: { [name: string]: any }, source: string = 'api'): Delta"
            "getBounds(index: number, length: number = 0): { left: number, top: number, height: number, width: number }"
        }
        return tools_list

    # def get_tutorial(self, document: str, content: str, stage: int) -> str:
    #     stage_list = self.get_toml_contents("tutorial_list", Path("/Users/cartercripe/dev/code/projects/worldweaver/backend/config/prompts"))
    #     unformatted_prompt = self.get_toml_contents("tutorial_prompt", Path("/Users/cartercripe/dev/code/projects/worldweaver/backend/config/prompts"))
    #     stage_title = self.get_stage_title(stage)
    #     formatted_prompt = unformatted_prompt.format(stages_list=stage_list, stage_title=stage_title)
    #
    #
    #     return "Not implimented"
    #
    # def get_toml_contents(self, file_name: str, file_dir_path: Path) -> str:
    #     if not file_dir_path.is_dir():
    #         raise NotADirectoryError(f"Prompt directory not found: {file_dir_path}")
    #
    #     fname, vers = file_name.split(":")
    #     with open(str(file_dir_path / f"{fname}.toml"), 'r') as file:
    #         toml_content = toml.load(file)
    #
    #     if vers == "latest":
    #         versions = [key for key in toml_content.keys() if key.startswith('v')]
    #         version = max(versions, key=lambda v: int(v[1:]))
    #     else:
    #         version = f"v{vers}"
    #     return toml_content[version]
    #
    # def get_stage_title(self, num: int) -> str:
    #     names = {
    #         # Section 1: Getting Started
    #         1: "Stage 1: Your Big Idea",
    #         2: "Stage 2: Working Title",
    #         3: "Stage 3: Genre & Flavor",
    #         4: "Stage 4: Main Vibe",
    #         5: "Stage 5: One-Sentence Pitch",
    #
    #         # Section 2: Worldbuilding Basics
    #         6: "Stage 6: Setting",
    #         7: "Stage 7: Time Period",
    #         8: "Stage 8: The Map",
    #         9: "Stage 9: The Environment",
    #         10: "Stage 10: Magic: Yes or No",
    #
    #         # Section 3: Worldbuilding Expanded
    #         11: "Stage 11: Magic Rules",
    #         12: "Stage 12: History Snapshot",
    #         13: "Stage 13: Groups & Cultures",
    #         14: "Stage 14: Government & Power",
    #         15: "Stage 15: Everyday Life",
    #         16: "Stage 16: Creatures",
    #         17: "Stage 17: Plants & Resources",
    #
    #         # Section 4: Characters
    #         18: "Stage 18: Your Hero",
    #         19: "Stage 19: What They Want",
    #         20: "Stage 20: What’s in Their Way",
    #         21: "Stage 21: Your Villain",
    #         22: "Stage 22: Why They Oppose",
    #         23: "Stage 23: Sidekick or Ally",
    #         24: "Stage 24: Other Important Characters",
    #         25: "Stage 25: Character Secrets",
    #
    #         # Section 5: Plot Basics
    #         26: "Stage 26: Choose a Story Shape",
    #         27: "Stage 27: Inciting Incident",
    #         28: "Stage 28: Turning Point #1",
    #         29: "Stage 29: Midpoint Twist",
    #         30: "Stage 30: Turning Point #2",
    #         31: "Stage 31: Climax",
    #         32: "Stage 32: Resolution",
    #
    #         # Section 6: Plot Expanded
    #         33: "Stage 33: Stakes",
    #         34: "Stage 34: Theme (Optional)",
    #         35: "Stage 35: Subplots",
    #         36: "Stage 36: Foreshadowing",
    #         37: "Stage 37: Scene List",
    #
    #         # Section 7: Writing Style
    #         38: "Stage 38: Point of View",
    #         39: "Stage 39: Tone",
    #         40: "Stage 40: Audience",
    #         41: "Stage 41: Length Goal",
    #         42: "Stage 42: Sample Paragraph"
    #     }
    #     return names.get(num, "Invalid stage number")
def do_tutorial(prompt: str) -> str:
    agent: Agent = Agent.get_agent("tutorial", "tutorial_prompt")
    return agent.invoke(prompt)

def do_character_dev(prompt: str):
    agent: Agent = Agent.get_agent("character", "character_prompt")
    return agent.invoke(prompt)


# Example usage
if __name__ == "__main__":
    ai = call_ai()
    text = "What are your opinions on the mining of rare resources?"
    response = ai.get_response("Respond like Director Krennic from star wars", text)
    print(response)