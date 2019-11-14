# Labby

## What is this

A bunch of AWS Lambda Functions for automating various processes related to the Lambda School Labs program.

## DAO

This little package is meant to abstract away some of the underlying technologies that make Labs tick. For example, much of our data is in Airtable, but not for long. The goal of the DAO layer is to insulate the functions a little to they don't need to call the Airtable client directly, but just see the output. This way, when we ditch Airtable, the functions won't need to change much.

## Where's the code

Packages (folders) are used to separate various capabilities. They are more or less organized by business function. The modules inside the packages should all basically relate to the business function described in the package.

## What do these packages do

### Mock Interviews

Mock interviews are an essential part of how Labs works. There's a process by which students are identified and scheduled for these interviews. The modules in this package help by notifying various parties to make sure the interview happens on schedule.

### Peer Reviews

Each week, students


aws secretsmanager create-secret --name labby-github-api-app-id --secret-string <Client ID>
https://github.com/organizations/Lambda-School-Labs/settings/apps/lambda-labs-labby

aws secretsmanager create-secret --name labby-github-api-key --secret-string file://${HOME}/Downloads/lambda-labs-labby.2019-10-04.private-key.pem

sls invoke local --function syncReposWithCodeClimate

aws secretsmanager create-secret --name labby-code-climate-api-key --secret-string <API KEY>

serverless plugin install --name serverless-cloudside-plugin

aws secretsmanager create-secret --name labby-airtable-api-key --secret-string <Airtable API Key>

aws secretsmanager create-secret --name labby-github-integration-id --secret-string <Integration ID>

aws secretsmanager create-secret --name labby-github-installation-id --secret-string <Installation ID>