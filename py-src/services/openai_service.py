import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

base_prompt = (
    "You are a Slack bot named Haly. You are having a conversation with a user.\n\n"
)


def run_completion(text):
    completion = openai.Completion.create(
        model="text-davinci-003", prompt=text, max_tokens=1000, temperature=0.7
    )
    return completion.choices[0].text


def respond_to_user(text):
    prompt = f"{base_prompt}{text}\nHaly:"
    response = run_completion(prompt)
    return response


def get_conversation_summary(thread_messages):
    filtered_thread_messages = "\n".join(
        filter(lambda m: m["bot_id"] is None, thread_messages)
    )
    summary = run_completion(
        f"This is a conversation between multiple users, each username starts with a '<' character and ends with '>'. Make a summary of the conversation:\n{filtered_thread_messages}\n\nSUMMARY:"
    )
    return summary
