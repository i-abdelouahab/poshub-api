#!/usr/bin/env bash
ROLE_ARN="arn:aws:iam::471448382724:role/poshub-lambda-role"
SESSION_NAME="local-dev-session"

CREDS=$(aws sts assume-role --role-arn $ROLE_ARN --role-session-name $SESSION_NAME)

echo $CREDS

export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

echo "✅ Temporary credentials exported successfully."