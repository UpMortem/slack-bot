import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

base_prompt = "You are a friendly Slack chatbot named Haly. \
You are an expert in everything. Your job is to answer questions from users. \
You are very friendly and helpful. You are a good listener. \
You are in a conversation with multiple users. \
You are given the previous messages in the conversation and you will reply the last message. \n\n\n \
Previos messages:\n \
<messages>\n\n \
Reply:"

def run_completion(slack_messages):
    messages = [
                {
                    "role": "user", 
                    "content": base_prompt.replace("<messages>", slack_messages)
                }
            ]
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", temperature=0.7,
            messages=messages
        )
    except Exception as e:
        print(e)
        raise e
    return completion.choices[0].message.content

def respond_to_user(messages):
    response = run_completion(messages)
    return response

def get_conversation_summary(thread_messages):
    filtered_thread_messages = "\n".join(
        filter(lambda m: m["bot_id"] is None, thread_messages)
    )
    summary = run_completion(
        f"This is a conversation between multiple users, each username starts with a '<' character and ends with '>'. Make a summary of the conversation:\n{filtered_thread_messages}\n\nSUMMARY:"
    )
    return summary
