# Sonarcloud.io

Sonar cloud is becoming an important resource for measuring code quality for our products, which allows us to better understand team and individual student capabilities.

## Gather sonarcloud Metrics

This function is responsible for periodically gathering and storing high level sonarcloud metrics for use by various reporting and operational tools.

Metrics:

- Maintainability Rating
- Coverage

This function is implemented using the fanout pattern, where SQS is used to queue up the list of repositories to be processed that are then processed in parallel batches by another Lambda function.

## Sonarcloud DAO

The DAO in this module enables easy access to the Sonarcloud Web API.
