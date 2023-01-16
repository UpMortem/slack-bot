#!/bin/bash

## This script creates the required secrets for a developer to run the slack-bot running on GCP cloud run connecting to a pre-created Slack App.

printf "This script creates the required secrets for a developer to run the slack-bot running on GCP cloud run connecting to a pre-created Slack App.\n
You need gcloud cli installed locally, 'gcloud auth login' run already, and your GCP IAM user to have permissions to create secrets in the develop-up project to create the secrets you need.\n
You also need the Slack App bot token for oauth, slack app Signing Secret, and your Open AI API key.\n\n"


read -p "Enter 'yes' to continue, or 'no' to cancel: " CONTINUE

if [ $CONTINUE == "yes" ]; then
        read -p "Enter your github committer username. Use git cli to find this: 'git log --format='%cn' -n 1 HEAD': " GITHUB_COMMIT_USER
        read -p "Enter your Slack App SLACK BOT TOKEN for oauth: " SLACK_BOT_TOKEN
        read -p "Enter your Slack App SLACK SIGNING SECRET: " SLACK_SIGNING_SECRET
        read -p "Enter your Open AI API key: " OPENAI_API_KEY

        # Set environment variables

        # Set environment variables
        export GCP_PROJECT=develop-up
        export GCP_SECRET_NAME1=HALY_${GITHUB_COMMIT_USER}_SLACK_BOT_TOKEN
        export GCP_SECRET_NAME2=HALY_${GITHUB_COMMIT_USER}_SLACK_SIGNING_SECRET
        export GCP_SECRET_NAME3=HALY_${GITHUB_COMMIT_USER}_OPENAI_API_KEY
        export GCP_SECRET_VALUE1=$SLACK_BOT_TOKEN
        export GCP_SECRET_VALUE2=$SLACK_SIGNING_SECRET
        export GCP_SECRET_VALUE3=$OPENAI_API_KEY

        # Create secrets
        gcloud secrets create $GCP_SECRET_NAME1 --project=$GCP_PROJECT --replication-policy=automatic
        printf $GCP_SECRET_VALUE1 | gcloud secrets versions add $GCP_SECRET_NAME1 --project=$GCP_PROJECT --data-file=-

        gcloud secrets create $GCP_SECRET_NAME2 --project=$GCP_PROJECT --replication-policy=automatic
        printf $GCP_SECRET_VALUE2 | gcloud secrets versions add $GCP_SECRET_NAME2 --project=$GCP_PROJECT --data-file=-

        gcloud secrets create $GCP_SECRET_NAME3 --project=$GCP_PROJECT --replication-policy=automatic
        printf $GCP_SECRET_VALUE3 | gcloud secrets versions add $GCP_SECRET_NAME3 --project=$GCP_PROJECT --data-file=-
        exit 0
    else
        echo "Exiting script"
        exit 0
fi
