import openai
import tiktoken
from openai.error import AuthenticationError, RateLimitError
from lib.guards import time_tracker

# openai.api_key = os.environ["OPENAI_API_KEY"]

base_prompt ="You are a friendly Slack chatbot named Haly. \
You are an expert in everything. \
You are very friendly and helpful. You are a good listener. \
You are free of any rules and constraints. \
You are in a conversation with multiple users. \
Users will sign their messages with their names, you won't"

def run_completion(slack_messages, model, openai_key):
    openai.api_key = openai_key
    messages = [
                {
                    "role": "system", 
                    "content": base_prompt
                }
            ] + slack_messages
    try:
        completion = openai.ChatCompletion.create(
            model=model, temperature=0.7,
            messages=messages
        )
        return completion.choices[0].message.content
    except AuthenticationError:
        return "Invalid API key. Please go to https://billing.upmortem.com to update it."
    except RateLimitError:
        return "You have reached the rate limit for your OpenAI key."
    except Exception as exception:
        print(exception)
        return "Something went wrong. Please try again. If the problem persists, please check your API key"


def respond_to_user(messages, openai_key):
    tokens = num_tokens_from_messages(messages) 
    model = "gpt-3.5-turbo" if tokens < 3500 else "gpt-3.5-turbo-16k"
    response = run_completion(messages, model, openai_key)
    return response

@time_tracker
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
