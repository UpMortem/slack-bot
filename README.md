# Haly AI

## Table of Contents
1. [Try for free](#try-for-free)
2. [Setting Up the Project](#setting-up-the-project)
3. [Running Tests](#running-tests)
4. [Deploying the Application](#deploying-the-application)
5. [Contributing to the Project](#contributing-to-the-project)

## Try for free
https://github.com/correct-repo-url.git

## Setting Up the Project

1. Set variables in .env file
2. Have venv installed `python3 -m pip install virtualenv` and create a venv at the root of your project using `python3 -m virtualenv -p python3 myvenv`
3. To enable the virtual environment run `source myvenv/bin/activate` on Linux/MacOS and `myvenv\Scripts\activate` on Windows - this opens up a terminal into the virtual environment.
4. Verify your python is isolated by typing `where python` in the above terminal
5. Run `pip install -r "requirements.txt"` to install dependencies in the same terminal
6. Run `flask --debug run` to start the dev server in the same terminal

If you use the --debug flag when running flask, the application will rebuild whenever the source code changes.

## Ngrok setup
You will need ngrok to test the Bot locally
- Go to https://ngrok.com/download and follow the instructions to install ngrok
- Open a terminal an run `ngrok http localhost:8080`
- Copy the forwarding url and go to you app setting in api.slack.com . Go to 'Event subscriptions'. Put your forwarding url + /slack/events in the Request URL input.
  - e.g: if your forwarindg url is https://3121-161-29-169-94.ngrok-free.app you put https://3121-161-29-169-94.ngrok-free.app/slack/events

## Running Tests

*Instructions for running tests go here*

## Deploying the Application

1. Setup a new release tag in github for the revision you want to release
2. Go to google cloud console 
3. Click on the instance you want to release to (or create new deployment through cloud build)
4. Click on `EDIT & DEPLOY NEW REVISION`
5. Update the tag version in the `Container image URL` field.
6. Scroll down and click deploy

## Contributing to the Project

*Guidelines for contributing to the project go here*
