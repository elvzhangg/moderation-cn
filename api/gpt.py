import re
from typing import ClassVar, Literal, Type

import openai
from pydantic import BaseModel
from filter_prompt import prompt

openai.api_key = ""

ChatModel = Literal["gpt-3.5-turbo"] | Literal["gpt-4"]
model_to_max_tokens = {
    "gpt-3.5-turbo": 4096,
    "gpt-4": 8096,
}




class Message(BaseModel):
    role: Literal["system"] | Literal["user"] | Literal["assistant"]
    content: str


class ChatGPT(BaseModel):
    messages: list[Message] = [
        Message(
            role="system",
            content=prompt,
        )
    ]
    prev_message_states: list[list[Message]] = []
    model: ChatModel = "gpt-4"

    @classmethod
    def from_system_message_content(cls, content: str, **kwargs):
        return cls(messages=[Message(role="system", content=content)], **kwargs)

    def chat(self, content: str, model: ChatModel | None = None):
        self.prev_message_states.append(self.messages)
        self.messages.append(Message(role="user", content=content))
        # response = call_chatgpt(self.messages_dicts, model=model)
        response = self.call_openai(model=model)
        self.messages.append(Message(role="assistant", content=response))
        return self.messages[-1].content

    def call_openai(self, model: ChatModel | None = None):
        if model is None:
            model = self.model
        messages_length = (
            sum([message.content.count(" ") for message in self.messages]) * 1.5
        )
        max_tokens = model_to_max_tokens[model] - int(messages_length) - 1000
        messages_raw = "\n".join([message.content for message in self.messages])
        result = (
            openai.ChatCompletion.create(
                model=model,
                messages=self.messages_dicts,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            .choices[0]
            .message["content"]
        )
        return result

    @property
    def messages_dicts(self):
        return [message.dict() for message in self.messages]

    def undo(self):
        if len(self.prev_message_states) > 0:
            self.messages = self.prev_message_states.pop()
        return self.messages
    
def get_moderation_status(user_input: str):
    model = ChatGPT()
    model.messages.append(Message(role="system", content=prompt))
    model.messages.append(Message(role="user", content=user_input))
    response = model.call_openai('gpt-3.5-turbo')
    if "DISALLOWED" in response or "sorry" in response:
        return False
    return True