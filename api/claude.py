import os
import re
from loguru import logger
import anthropic
from api.filter_prompt import prompt

STOPWORD = "</filter_status>"

def get_claude_response(user_input, max_tokens_to_sample: int = 200, api_key: str = ''):
    # Chat with claude twice and get a response in the second one
    c = anthropic.Client(api_key)
    formatted_prompt = f"{anthropic.HUMAN_PROMPT}{prompt.format(input=user_input)}{anthropic.AI_PROMPT}"
    logger.info(f"Sending request to claude: {formatted_prompt}")
    resp = c.completion(
        prompt=formatted_prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT, STOPWORD],
        model="claude-v1",
        max_tokens_to_sample=max_tokens_to_sample,
    )
    logger.info(resp)
    completion = resp['completion'] + STOPWORD
    regex_search = re.search(r'<filter_status>(.*?)</filter_status>', completion)
    if regex_search is None:
        return "DISALLOWED"
    filter_status = regex_search.group(1).strip()
    logger.info(f"Filter status: {filter_status}")
    return filter_status

def get_is_text_safe(user_input: str, api_key: str = ''):
    return not "DISALLOWED" in get_claude_response(user_input, api_key=api_key)

