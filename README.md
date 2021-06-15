# Labby

Labby is a growing collection of automation functions that support Lambda School Labs operations.

## Architecture

Labby is a serverless application built on the [Serverless Framework](https://serverless.com) currently deployed to AWS. Labby uses various AWS services to allow for scale and reliability.

## Packages

The packages in Labby are broken up by the various services that Labby manages. Though, given that Labby enables integration between various services, the code in each package will probably reference other services.

See the README in each package for more details.

- `labsaws`: For talking to the AWS API
- `labscodeclimate`: For talking to the Code Climate API
- `labssonarcloud`: For talking to the Sonar Cloud API
- `labsdao`: A data access layer for retrieving various Labs-specific entities (e.g. students, projects)
- `labsslack`: For talking to the Slack API
- `labssearchlight`: For talking to the Searchlight API
- `teambuilding`: The Labs Team Builder algorithm

## Configuration

Labby needs access to all sorts of APIs and data stores, which require secrets. All secrets are managed via AWS Secrets Manager.

Adding a secret:

```shell
aws secretsmanager create-secret --name <secret-name> --secret-string <secret-value>
```

Here are the secrets that need to be available for Labby:

### Github Credentials

Labby interacts with Github as a [Github App](https://developer.github.com/apps/):

| Secret Name                  | Secret Value                                        |
| ---------------------------- | --------------------------------------------------- |
| labby-github-api-app-id      | Client ID from the app settings                     |
| labby-github-api-key         | The downloaded app private key                      |
| labby-github-integration-id  | The integration ID created when installing the app  |
| labby-github-installation-id | The installation ID created when installing the app |

### Code Climate Credentials

Labby interacts with the Code Climate API using an [API key](https://developer.codeclimate.com/#overview):

| Secret Name                | Secret Value         |
| -------------------------- | -------------------- |
| labby-code-climate-api-key | Code Climate API key |

### Airtable Credentials

Labby interacts with Airtable using an [API key](https://airtable.com/api):

| Secret Name            | Secret Value     |
| ---------------------- | ---------------- |
| labby-airtable-api-key | Airtable API key |

## Labby Assets

The `assets` folder contains various static assets for use by the functions. Be aware that during deployment the `serverless-s3-deploy` plugin will automatically ship _everything in the assets folder_ to a _public, readable by the whole wide world web_ S3 bucket.

## Running Local

### pyenv + pipenv

This project uses pyenv for ensuring Python versions are consistent and pipenv for handling dependencies.

### AWS Profiles

> If you are using aws profiles then you must have an env var AWS_PROFILE set to the profile name. (might as well add AWS_REGION to be safe)
>
> `export AWS_PROFILE=labby && export AWS_REGION=us-east-1`

- install [pipenv](https://github.com/pypa/pipenv)
- `pipenv install --dev`
- `pipenv shell`
- `python --version` # Python 3.7.3

TODO: Setup Serverless framework for python

- [Getting Started](https://serverless.com/framework/docs/getting-started/)
- `npx install serverless`
- [config]
- `sls invoke cloudside -f codeclimate_enqueue_all_product_repos`
