import json

from google import genai

from config import config


class Gemini:

    def __init__(self):

        self.client = genai.Client(
            api_key=config.GEMINI_API_KEY
        )

        self.model = config.MODEL_NAME

    def ask(self, prompt: str):

        response = self.client.models.generate_content(

            model=self.model,

            contents=prompt

        )

        return response.text

    def ask_json(self, prompt: str):

        prompt += """

Return ONLY valid JSON.

Do not use markdown.

"""

        text = self.ask(prompt)

        text = text.replace("```json", "")

        text = text.replace("```", "")

        return json.loads(text)