from __future__ import annotations

import os

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Markdown
from textual.reactive import var, reactive

import openai

openai.api_key=os.environ.get("OPENAI_API_KEY")

class ChatContent(Markdown):
    content = reactive("")
    history = var("")
    prompt = var("")
    response = var("")

    def receive_response(self, prompt, response):
        self.prompt = prompt
        self.response = response

    def parse_response(self):
        for chunk in self.response:
            yield chunk['choices'][0]['delta'].get('content', '')

    def update_content(self):
        try:
            self.content += next(self.parse_response())
        except:
            pass

    def on_mount(self):
        self.set_interval(1 / 100, self.update_content)

    def watch_content(self, content):
        if content != "":
            self.update(f"{self.prompt}\n\n================\n\n**ChatGPT**: {content}\n\n")

class ChatbotApp(App):
    """Chatbot app"""

    CSS_PATH = "chatbot.css"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter your request")
        yield VerticalScroll(ChatContent(id="results"), id="results-container")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        # Clear the Input
        self.query_one(Input).action_delete_left_all()
        self.query_one(Input).action_delete_right_all()

        chat_content = self.query_one(ChatContent)

        if message.value:
            prompt = message.value
            chat_content = self.query_one(ChatContent)
            messages = [
                {
                'role': 'system',
                'content': 'You are a helpful assistant.'
                }, {
                'role': 'user',
                'content': prompt
                }
            ]
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo', messages=messages, stream=True, temperature=1
            )
            chat_content.receive_response(prompt, response)
            if chat_content.content != "":
                chat_content.history += f"User: {prompt}\n\nChatGPT: {chat_content.content}\n\n"
            chat_content.content = ""

if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
