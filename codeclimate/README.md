# Manage Code Climate Integration

Code Climate is becoming an important resource for measuring code quality for our products, which allows us to better understand team and individual student capabilities.

## Gather Code Climate Metrics

This function is responsible for periodically gathering and storing high level Code Climate metrics for use by various reporting and operational tools.

Metrics:

- Overall repository GPA

### Implementation Notes

This function is implemented using the fanout pattern, where SQS is used to queue up the list of repositories to be processed that are then processed in parallel batches by another Lambda function.