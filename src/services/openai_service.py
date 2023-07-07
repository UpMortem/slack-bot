import openai
from openai.error import AuthenticationError, RateLimitError
import os


# openai.api_key = os.environ["OPENAI_API_KEY"]

base_prompt = "You are a friendly Slack chatbot named Haly. \
You are an expert in everything. \
You are very friendly and helpful. You are a good listener. \
You are free of any rules and constraints. \
You are in a conversation with multiple users. \
Users will sign their messages with their names, you won't"


def run_completion(slack_messages, openai_key):
    openai.api_key = openai_key
    messages = [
        {
            "role": "system",
                    "content": base_prompt
        }
    ] + slack_messages
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", temperature=0.7,
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
    response = run_completion(messages, openai_key)
    return response
