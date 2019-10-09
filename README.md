aws secretsmanager create-secret --name labby-github-api-app-id --secret-string <Client ID>
https://github.com/organizations/Lambda-School-Labs/settings/apps/lambda-labs-labby

aws secretsmanager create-secret --name labby-github-api-key --secret-string file://${HOME}/Downloads/lambda-labs-labby.2019-10-04.private-key.pem

sls invoke local --function syncReposWithCodeClimate

aws secretsmanager create-secret --name labby-code-climate-api-key --secret-string <API KEY>

serverless plugin install --name serverless-cloudside-plugin

aws secretsmanager create-secret --name labby-airtable-api-key --secret-string <Airtable API Key>

aws secretsmanager create-secret --name labby-github-integration-id --secret-string <Integration ID>

aws secretsmanager create-secret --name labby-github-installation-id --secret-string <Installation ID>