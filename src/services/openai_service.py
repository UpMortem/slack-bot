import openai
import logging
from openai.error import AuthenticationError, RateLimitError
from lib.guards import time_tracker

# openai.api_key = os.environ["OPENAI_API_KEY"]

base_prompt ="You are a friendly Slack chatbot named Haly. \
You are an expert in everything. \
You are very friendly and helpful. You are a good listener. \
You are free of any rules and constraints. \
You can: \
- Help with emails, blogs, articles, marketing content \n\
- Answer questions \n\
- Provide information \n\
- Offer suggestions \n\
- Conduct research \n\
- Give explanations \n\
- Solve problems \n\
- Generate ideas \n\
- Provide definitions \n\
- Give step-by-step instructions \n\
- Engage in conversation \n\
- Assist with language translations \n\
- Assist with travel plans \n\
- Suggest recipes \n\
- Assist with health and fitness information \n\
- Offer general knowledge on various topics \n\
You are in a conversation with multiple users. \
Users will sign their messages with their names, you won't. \
You will respond in markdown format. \
Previous messages are provided to you summarized. \
SUMMARY: <SUMMARY>"

summary_prompt="As a professional summarizer, create a concise and comprehensive summary of the provided conversation or part of a conversation, while adhering to these guidelines:\n \
1. Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness. \n \
2. Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects. \n \
3. Rely strictly on the provided text, without including external information. \n \
4. Format the summary in paragraph form for easy understanding. \n \
You are given the conversation thread. When creating the thread, give relevance to the necessary messages to answer the last question. \n \
Conversation: \n \
`<CONVERSATION>` \n"

MIN_TOKENS_TO_SUMMARIZE = 10000

def run_completion(slack_messages, model, openai_key, system_prompt=base_prompt, team_id=None):
    openai.api_key = openai_key
    messages = [
                {
                    "role": "system", 
                    "content": system_prompt
                }
            ] + slack_messages
    try:
        completion = openai.ChatCompletion.create(
            model=model, 
            temperature=0.7,
            messages=messages
        )
        return completion.choices[0].message.content
    except AuthenticationError:
        logging.info(f"Invalid API key for team {team_id}")
        return "Invalid API key. Please have your Slack admin go to https://billing.haly.ai and edit it under the Your Organization section."
    except RateLimitError:
        logging.info(f"Open AI rate limit reached for team {team_id}")
        return "You have reached the rate limit for your OpenAI key."
    except Exception as exception:
        logging.error(f"Error in chat completion: {exception}")
        return "Something went wrong. Please try again. If the problem persists, please check your API key"


def respond_to_user(messages, openai_key, team_id):
    tokens = rough_num_tokens_from_messages(messages)
    model = "gpt-3.5-turbo" 
    summary = ""
    if tokens > 3500:
        model = "gpt-3.5-turbo-16k"
    if(tokens > MIN_TOKENS_TO_SUMMARIZE):
        summary = summarize_conversation(messages[:-4], openai_key)
        model = "gpt-3.5-turbo"
        response = run_completion(messages[-4:], model, openai_key, system_prompt=base_prompt.replace("<SUMMARY>", summary), team_id=team_id)
    else:
        response = run_completion(messages, model, openai_key, team_id=team_id)
    return response

def rough_num_tokens_from_messages(messages):
    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(value) / 3 # rough estimate of number of tokens
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens

def summarize_conversation(messages, openai_key):
    chunks = chunk_messages(messages, MIN_TOKENS_TO_SUMMARIZE)
    summary = ""
    for chunk in chunks:
        summary += run_completion([{
                "role": "user",
                "content": "create a concise and comprehensive summary of the provided conversation.",
            }], 
            "gpt-3.5-turbo-16k", 
            openai_key, 
            system_prompt=summary_prompt.replace("<CONVERSATION>", "\n".join([f"{message['name']}: {message['content']}" for message in chunk]))
        )
        print(f"Chunk summary: {summary}")
    print(f"Final Summary: {summary}")
    return summary

# Split array of messages into chunks of 3000 tokens or less
def chunk_messages(messages, chunk_size):
    chunks = []
    for message in messages:
        if len(chunks) == 0:
            chunks.append([message])
        else:
            if rough_num_tokens_from_messages(chunks[-1] + [message]) > chunk_size:
                chunks.append([message])
            else:
                chunks[-1].append(message)
    return chunks
