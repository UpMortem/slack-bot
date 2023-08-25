# Haly AI

## Try for free
https://haly.ai

## Setup for dev
- Go to your command prompt
- activate your virtual envioronment
- Set variables in .env file
- Variables should include Slack bot token, signing secret, open ai key, Server ,and API
- Have venv installed `python3 -m pip install virtualenv` and create a venv at the root of your project using `python3 -m virtualenv -p python3 myvenv`
- To enable the virtual environment run `source myvenv/bin/activate` on Linux/MacOS and `myvenv\Scripts\activate` on Windows - this opens up a terminal into the virtual environment.
- verify your python is isolated by typing `where python` in the above terminal
- before running your bot make sure that your index.py file is in the correct directory otherwise you will receive an error stating "could not import flask" 
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

 - Setup a new release tag in github for the revision you want to release
 - Got to google cloud console 
 - Click on the instance you want to release to (or create new deployment through cloud build)
 - Click on `EDIT & DEPLOY NEW REVISION`
 - Update the tag version in the `Container image URL` field.
 - Scroll down and click deploy
