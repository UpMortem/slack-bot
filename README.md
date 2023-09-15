# Haly AI - Your Friendly Chatbot Companion

![Haly](images/github_readme.png)

## Welcome to Haly!

**Haly** is here to revolutionize the way you communicate and seek information. With its friendly and helpful nature, Haly is more than just a chatbot - it's your ultimate companion in the digital world.

## What Can Haly Do?

Haly is an expert in everything - from providing answers and explanations, to generating ideas and assisting with various tasks. Here are just a few things Haly can help you with:

- **Semantic Search (SmartSearch)**: Ask questions about your organization and Haly will tell you an answer based on previous public channel messages and who are the subject matter experts.
- **Emails, Blogs, and Marketing Content**: Need assistance with writing? Haly is at your service, providing suggestions, editing, and even helping with translations.
- **Information and Research**: Curious about a specific topic? Haly can provide you with accurate information and conduct in-depth research to satisfy your curiosity.
- **Problem Solving and Troubleshooting**: Stuck with a difficult problem? Haly loves challenges and is always ready to help you find the best solution.
- **Recipes and Health & Fitness**: Looking for a delicious recipe or need some advice on staying fit? Haly has got you covered with a wide range of suggestions and information.
- **Travel Planning**: Need help with your travel plans? Haly can assist you in finding the best destinations, booking accommodations, and even suggesting local attractions.

## Why Choose Haly?

Haly is not just another chatbot - it's a personal assistant that truly cares about your needs. Here's why you should give Haly a try:

- **Friendly and Engaging**: Haly's warm and approachable personality makes every conversation enjoyable. You'll feel like you're chatting with a good friend.
- **Expert in Everything**: Whether you need help with writing, research, problem-solving, or anything else, Haly has the knowledge and expertise to assist you.
- **Always Available**: Haly is there for you 24/7, ready to provide assistance whenever you need it. Say goodbye to waiting for human help.
- **Efficient and Reliable**: Haly is fast, accurate, and reliable. You can trust Haly to deliver high-quality results every time.

## Get Started with Haly Today!

Ready to experience the power of Haly? Join the growing community of Haly users and see how this friendly chatbot can enhance your digital life. Simply visit our website https://haly.ai or integrate Haly into Slack following the instructions in this README, and let the conversation begin!
Note: Haly is constantly learning and improving, so don't hesitate to provide feedback and suggestions. Together, we can make Haly even better!

## Try for free

https://haly.ai

## Setup for dev

### Prereqs

1. You must have a Slack organization where either you or an administrator can approve a new application.
2. The ability to git clone a repo and run commands in either a Windows, Mac, or Linux terminal.
3. Install [python](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/).

### Create your Slack bot:

1. Go to https://api.slack.com/apps and hit the "Create New App" green button. Select "From an app manifest" option.
   <img width="425" alt="image" src="https://user-images.githubusercontent.com/15027870/218860230-a8c4c679-fe75-45cc-a6bc-25229dd1610b.png">

---

2. Choose workspace from dropdown if needed and paste the following content in the manifest. Hit Next button. Review the OAuth and Features tabs then hit Create.
   <img width="425" alt="image" src="https://user-images.githubusercontent.com/15027870/218860631-6ffd3a66-463e-4c90-85f9-701ba69d3bb5.png">

```
{
    "display_information": {
        "name": "Haly",
        "description": "AI Assistant",
        "background_color": "#2f3133",
        "long_description": "I'm Haly, your friendly Slack chatbot. I'm here to help you with any questions or problems you might have. I'm an expert in everything, so feel free to ask me anything. I'm a good listener and always ready to assist you. Just type your question or request, and I'll do my best to provide you with the information you need. You can direct message me or add me to a public channel. Just tag me to talk with me with @Haly."
    },
    "features": {
        "app_home": {
            "home_tab_enabled": true,
            "messages_tab_enabled": true,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "Haly",
            "always_online": true
        }
    },
    "oauth_config": {
        "redirect_urls": [
            "https://localhost:5173/slack-auth"
        ],
        "scopes": {
            "bot": [
                "app_mentions:read",
                "channels:history",
                "channels:join",
                "channels:read",
                "chat:write",
                "groups:history",
                "groups:write",
                "im:history",
                "im:read",
                "im:write",
                "mpim:history",
                "mpim:read",
                "mpim:write",
                "users:read"
            ]
        }
    },
    "settings": {
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```

---

3. Select `Basic information` tab from the left nav bar, scroll down and make sure to save the "Signing Secret" for later.
   <img width="711" alt="image" src="https://user-images.githubusercontent.com/15027870/218861139-fa549cce-73e0-457c-ba00-a3cdb96372c5.png">

Scroll down further and use [Haly Profile Image](https://github.com/UpMortem/slack-bot/assets/469387/490a891e-379e-4e5c-9f31-4699dce78e01) for her App icon or select your own if you wish.

---

4. Next, select `OAuth & Permissions` tab from the left nav bar, under `OAuth Tokens for Your Workspace` section, hit `Install to Workspace` and follow the instructions there.
   <img width="652" alt="image" src="https://user-images.githubusercontent.com/15027870/218863134-e9d7badc-0442-4c09-9417-d6e8e0267c6b.png">

---

5. After installing, you will find a Bot user OAuth token. Save this for later use.
   ![image](https://github.com/UpMortem/slack-bot/assets/5354324/7d866eee-a7e6-4059-b422-bae8ac9016a3)

### Configure your project

- In a terminal git clone the project. [See the offical documentation if you do not know how to do this](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).
- cd in the slack-bot directory
- Create a new .env file. You can use the touch command (touch .env) to create the file. Then use your favorite editor to edit it.
- If you only want to use Haly for your own workspace, you can use it in standalone mode. Put the following in your .env file:

```
# SLACK BOT
SLACK_BOT_TOKEN=xoxb-your-oauth-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
# OPENAI
OPENAI_API_KEY=your-openai-api-key
# SERVER
FLASK_APP=src/index.py
FLASK_RUN_HOST=localhost
FLASK_RUN_PORT=8080
# API
API_SHARED_SECRET=not-needed-for-standalone
API_BASE_URL=not-needed-for-standalone

LOG_LEVEL=DEBUG
STANDALONE=true
SLACK_USER_ID=U01JZQZQZQZ # Put a your workspace admin user ID if you know it
```

- Update SLACK_BOT_TOKEN (OAuth token), SLACK_SIGNING_SECRET, OPENAI_API_KEY ([Click here to learn how to get an API key from OpenAI](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt)), and SLACK_USER_ID ([Click here how to get your Slack user ID](https://www.workast.com/help/article/how-to-find-a-slack-user-id/))
- Have venv installed `python3 -m pip install virtualenv`
- Create a venv at the root of the slack-bot project using `python3 -m virtualenv -p python3 myvenv`
- To enable the virtual environment run `source myvenv/bin/activate` on Linux/MacOS and `myvenv\Scripts\activate` on Windows - this opens up a terminal into the virtual environment.
- verify your python is isolated by typing `where python` in the above terminal. It should show a python path within the project.
- Run `pip install -r "requirements.txt"` to install dependencies in the same terminal
- Run `flask --debug run` to start the dev server in the same terminal

If you use the --debug flag when running flask, the application will rebuild whenever the source code changes.

## Ngrok setup

You will need ngrok to test the Bot locally

- Go to https://ngrok.com/download and follow the instructions to install ngrok
- Open a terminal an run `ngrok http localhost:8080`
- Copy the forwarding url that starts with _https_ and go to you app setting in api.slack.com . Go to 'Event subscriptions'. Put your forwarding url + /slack/events in the Request URL input.
  - e.g: if your forwarindg url is https://3121-161-29-169-94.ngrok-free.app you put https://3121-161-29-169-94.ngrok-free.app/slack/events
- Subscribe to the neccesary bot events
  ![image](https://github.com/UpMortem/slack-bot/assets/5354324/f46f93f3-8713-432f-812f-1ba6218fc07f)

## Releases

- Cloud build trigger will run every time you push a git tag that matches `^v.*$`

## Running the tests

To ensure the quality and reliability of the application, we have a suite of unit tests. These tests can be run using the unittest module in Python. To run the tests, navigate to the root directory of the project and run the following command:

```bash
python -m unittest discover -s src/tests
```

This command will discover and run all the test cases that are present in the `src/tests` directory.
