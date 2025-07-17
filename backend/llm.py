from dataclasses import replace
from sys import getallocatedblocks

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


class Call_Ai:
    def __init__(self):
        """Initialize the call_ai class"""
        pass

    def get_stub(self, content):
        if content == "insert":
            return {
                "type": "tool",
                "tool": "insert",
                "index": 0,
                "text": "You shall not pass!\n",
                "style": "bold",
                "value": True,
                "source": "api"
            }

        elif content == "set":
            return {
            "type": "tool",
            "tool": "set",
            "text": (
                "Calm. Kindness. Kinship. Love. \nI’ve given up all chance at inner peace. I’ve made my mind a sunless space. I share my dreams with ghosts. I wake up every day to an equation I wrote 15 years ago from which there’s only one conclusion, I’m damned for what I do. My anger, my ego, my unwillingness to yield, my eagerness to fight, they’ve set me on a path from which there is no escape. I yearned to be a savior against injustice without contemplating the cost and by the time I looked down there was no longer any ground beneath my feet.\nWhat is my sacrifice?\nI’m condemned to use the tools of my enemy to defeat them. I burn my decency for someone else’s future. I burn my life to make a sunrise that I know I’ll never see. And the ego that started this fight will never have a mirror or an audience or the light of gratitude. \nSo what do I sacrifice?\n Everything!\n"
            ),
            "source": "api"
        }

        elif content == "get":
            return {
            "type": "tool",
            "tool": "get",
            "index": 0,
            "length": 29
        }

        elif content == "getall":
            return {
            "type": "tool",
            "tool": "getall",
            "index": 0
        }

        elif content == "update":
            return {
            "type": "tool",
            "tool": "update",
            "delta": {
                "ops": [
                    {"delete": 29},
                    {"insert": "Updated!"}
                ]
            },
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
            "index": 0,
            "length": "quill.getLength()",
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

        elif content == "bounds":
            return {
            "type": "tool",
            "tool": "bounds",
            "index": 0,
            "length": 29
        }

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



# Example usage
if __name__ == "__main__":
    ai = Call_Ai()
    text = "What are your opinions on the mining of rare resources?"
    response = ai.get_response("Respond like Director Krennic from star wars", text)
    print(response)