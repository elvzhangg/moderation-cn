from loguru import logger
import modal
import os
from pydantic import ValidationError  # type: ignore
from typing import Dict

# from api.gpt import get_moderation_status
from api.claude import get_is_text_safe

stub = modal.Stub("get-text-moderation-status")
image = modal.Image.debian_slim().pip_install("openai", "anthropic", "loguru")
secrets = [
    modal.Secret.from_name("content-mod-openai"),
    modal.Secret.from_name("anthropic"),
]

@stub.webhook(method="POST", image=image, secrets=secrets)
def moderation_webhook(raw_request: Dict):
    logger.info(f"Received request: {raw_request}")
    user_input = raw_request["text"]
    logger.warning("User input was: ", user_input)
    if user_input == "ping":
        return {"safe": True}
    if get_is_text_safe(user_input, os.environ["ANTHROPIC_API_KEY"]):
        return {"safe": True}
    else:
        return {"safe": False}
