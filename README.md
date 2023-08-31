# Haly AI

## Try for free
https://haly.ai

## Setup for dev

### Create your Slack bot:
1. Create a new slack app from an app manifest file under customers organization.
<img width="425" alt="image" src="https://user-images.githubusercontent.com/15027870/218860230-a8c4c679-fe75-45cc-a6bc-25229dd1610b.png">

2. Choose org from dropdown if needed and paste the following content in the manifest. Hit Create button
<img width="425" alt="image" src="https://user-images.githubusercontent.com/15027870/218860631-6ffd3a66-463e-4c90-85f9-701ba69d3bb5.png">

```
{
    "display_information": {
        "name": "Haly Master",
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
            "display_name": "Haly Master",
            "always_online": true
        }
    },
    "oauth_config": {
        "redirect_urls": [
            "https://localhost:5173/slack-auth",
            "<YOUR_AUTH0_URL>/login/callback"
        ],
        "scopes": {
            "bot": [
                "app_mentions:read",
                "channels:history",
                "chat:write",
                "groups:history",
                "im:history",
                "im:read",
                "im:write",
                "mpim:history",
                "mpim:read",
                "mpim:write",
                "users:read",
                "groups:write",
                "channels:read",
                "groups:read"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "<YOUR_NGROK_URL>/slack/events",
            "bot_events": [
                "app_home_opened",
                "app_mention",
                "message.im",
                "tokens_revoked"
            ]
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```

3. Select `Basic information` tab from the left nav bar, scroll down and make sure to note down signing secret or atleast remember where to get it again. 
<img width="711" alt="image" src="https://user-images.githubusercontent.com/15027870/218861139-fa549cce-73e0-457c-ba00-a3cdb96372c5.png">

4. Next, select `OAuth & Permissions` tab from the left nav bar, under `OAuth Tokens for Your Workspace` section, hit `Install to Workspace` and follow the instructions there.
<img width="652" alt="image" src="https://user-images.githubusercontent.com/15027870/218863134-e9d7badc-0442-4c09-9417-d6e8e0267c6b.png">

5. After installing, you will find a Bot user OAuth token
![image](https://github.com/UpMortem/slack-bot/assets/5354324/7d866eee-a7e6-4059-b422-bae8ac9016a3)

Copy this or remember where to find it.

6. Add these as latest versions of secrets in haly-pwc deployment and redeploy

7. Next, select `OAuth & Permissions` tab in api.slack.com and verify url in the top banner

8. you should be able to talk to haly in our clients slack org

### Configure your project
- Set variables in .env file
- Clone the repository `git clone https://github.com/correct-repo-url.git`
- Have venv installed `python3 -m pip install virtualenv` and create a venv at the root of your project using `python3 -m virtualenv -p python3 myvenv`
- To enable the virtual environment run `source myvenv/bin/activate` on Linux/MacOS and `myvenv\Scripts/activate` on Windows - this opens up a terminal into the virtual environment.
- verify your python is isolated by typing `where python` in the above terminal
- Run `pip install -r "requirements.txt"` to install dependencies in the same terminal
- Run `flask --debug run` to start the dev server in the same terminal

If you use the --debug flag when running flask, the application will rebuild whenever the source code changes.

## Ngrok setup
You will need ngrok to test the Bot locally
- Go to https://ngrok.com/download and follow the instructions to install ngrok
- Open a terminal an run `ngrok http localhost:8080`
- Copy the forwarding url and go to you app setting in api.slack.com . Go to 'Event subscriptions'. Put your forwarding url + /slack/events in the Request URL input.
  - e.g: if your forwarindg url is https://3121-161-29-169-94.ngrok-free.app you put https://3121-161-29-169-94.ngrok-free.app/slack/events

## release

 - Cloud build trigger will run every time you push a git tag that matches `^v.*$`
