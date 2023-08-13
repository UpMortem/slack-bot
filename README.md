# Haly AI

## Try for free
https://haly.ai

## Setup for dev

- Set variables in .env file
- Have venv installed `python3 -m pip install virtualenv` and create a venv at the root of your project using `python3 -m virtualenv -p python3 myvenv`
- To enable the virtual environment run `source myvenv/bin/activate` on Linux/MacOS and `myvenv\Scripts\activate` on Windows - this opens up a terminal into the virtual environment.
- verify your python is isolated by typing `where python` in the above terminal
- Run `pip install -r "requirements.txt"` to install dependencies in the same terminal
- Run `flask --debug run` to start the dev server in the same terminal

If you use the --debug flag when running flask, the application will rebuild whenever the source code changes.

## release

 - Setup a new release tag in github for the revision you want to release
 - Got to google cloud console 
 - Click on the instance you want to release to (or create new deployment through cloud build)
 - Click on `EDIT & DEPLOY NEW REVISION`
 - Update the tag version in the `Container image URL` field.
 - Scroll down and click deploy
