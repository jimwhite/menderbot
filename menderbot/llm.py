import os

from openai import Client
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from menderbot.config import has_llm_consent, load_config

openai_client: Client = None

INSTRUCTIONS = (
    """You are helpful electronic assistant with knowledge of Software Engineering."""
)

# MODEL = "gpt-4"
MODEL = "gpt-4-1106-preview"
TEMPERATURE = 0.5
MAX_TOKENS = 1000
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10

__key_env_var = "OPENAI_API_KEY"


def key_env_var() -> str:
    return __key_env_var


def init_openai():
    # pylint: disable-next=[global-statement]
    global openai_client
    global __key_env_var
    if has_llm_consent():
        config = load_config()
        openai_config = config.get("apis", {}).get("openai", {})
        __key_env_var = openai_config.get("api_key_env_var", "OPENAI_API_KEY")
        organization_env_var = openai_config.get(
            "organization_env_var", "OPENAI_ORGANIZATION"
        )
        openai_client = Client(
            api_key=os.getenv(__key_env_var),
            organization=os.getenv(organization_env_var),
            base_url=openai_config.get("api_base", "https://api.openai.com/v1"),
        )


init_openai()


def is_test_override() -> bool:
    return (
        os.getenv(key_env_var())
        == "sk-TEST00000000000000000000000000000000000000000000"
    )


def has_key() -> bool:
    return os.getenv(key_env_var(), "") != ""


def override_response_for_test(messages) -> str:
    del messages
    return "<LLM Output>"


def is_debug():
    return os.getenv("DEBUG_LLM", "0") == "1"


@retry(wait=wait_random_exponential(min=3, max=90), stop=stop_after_attempt(3))
def get_response(
    instructions: str, previous_questions_and_answers: list, new_question: str
) -> str:
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        {"role": "system", "content": instructions},
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
    # add the new question
    messages.append({"role": "user", "content": new_question})

    if is_debug():
        print("=== sending to LLM ===")
        for message in messages:
            print(message["role"], message["content"])
        print("===")
    if is_test_override():
        return override_response_for_test(messages)
    completion = openai_client.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content


def unwrap_codeblock(text):
    return text.strip().removeprefix("```").removesuffix("```")
