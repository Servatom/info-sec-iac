# IaC

This repositories contains the some Infra that would be needed for creating the watchdog.
- iam-check.py => This is the lambda function that would be used to check the IAM users and roles. This would trigger the handler.py when there is a change which would send a webhook so that the activity gets registered

- clickhouse.py => This sets up the clickhouse ec2 on AWS.