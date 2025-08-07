from dataclasses import replace
from sys import getallocatedblocks

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


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
    ai = call_ai()
    text = "What are your opinions on the mining of rare resources?"
    response = ai.get_response("Respond like Director Krennic from star wars", text)
    print(response)