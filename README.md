# Labby

## Overview

Labby is a growing collection of automation functions that support Lambda Labs operations.

## Architecture

Labby is a serverless application built on the [Serverless Framework](https://serverless.com) currently deployed to AWS. Labby uses various AWS services to allow for scale and reliability.

## Packages

The packages in Labby are broken up by the various services that Labby manages. Though, given that Labby enables integration between various services, the code in each package will probably reference other services.

See the README in each package for more details.

- Github: Manages provisioning and access to repositories based on active projects and team membership.
- Code Climate: Labs uses Code Climate to assess code quality, Labby helps integrate with Code Climate and gathers metrics.
- Slack: Allows Labby to interact with students and staff via Slack
- Mock Interviews: Labby helps with the Labs Mock Interview process
- Peer Reviews: Labby monitors peer review submissions (or lack thereof) to remind students and staff to submit their reviews.
- Labs Data: Much of Labby's activities are driven by data produced by operational activities in Labs.

## Configuration

Labby needs access to all sorts of APIs and data stores, which require secrets. These secrets are managed via AWS Secrets Manager.

Adding a secret:

```shell
aws secretsmanager create-secret --name <secret-name> --secret-string <secret-value>
```

Here are the secrets that need to be available for Labby:

### Github Credentials

Labby interacts with Github as a [https://developer.github.com/apps/](Github App):

Secret Name: labby-github-api-app-id
Secret Value: Client ID from the app settings (https://github.com/organizations/Lambda-School-Labs/settings/apps/lambda-labs-labby)

Secret Name: labby-github-api-key
Secret Value: The downloaded app private key (e.g. file://${HOME}/Downloads/lambda-labs-labby.2019-10-04.private-key.pem)

Secret Name: labby-github-integration-id
Secret Value: The integration ID created when installing the app

Secret Name: labby-github-installation-id
Secret Value: The installation ID created when installing the app

### Code Climate Credentials

Labby interacts with the Code Climate API using an [https://developer.codeclimate.com/#overview](API key):

Secret Name: labby-code-climate-api-key
Secret Value: Code Climate API key

### Airtable Credentials

Labby interacts with Airtable using an [API key](https://airtable.com/api):

Secret Name: labby-airtable-api-key
Secret Value: Airtable API key
