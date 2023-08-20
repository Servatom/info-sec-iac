from pulumi_aws import lambda_, iam, get_region, cloudwatch
from pulumi_aws.cloudwatch import get_event_target

# Start by creating an IAM role for the lambda function.
role = iam.Role('iamWatchDogLambda', assume_role_policy='''{
    "Version": "2012-10-17",
    "Statement": [
        { 
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}\n''')

policy = iam.RolePolicy('iamWatchDogLambdaPolicy',
                        role=role.id,
                        policy=pulumi.Output.all(role.arn).apply(
                            lambda args: '''
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:%s:*:*" % args[0]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": ["arn:aws:logs:%s:*:log-group:/aws/lambda/%s:*" % (args[0], args[1])]
        }
    ]
}
''' % (get_region().name, 'iamWatchDogLambda')))

# Then, create your lambda function.
lambda_func = lambda_.Function('mylambdaFunc',
                               role=role.arn,
                               runtime="python3.8",
                               handler="handler.main",
                               code=pulumi.AssetArchive({
                                   '.': pulumi.FileArchive('./app')
                               }))

# Now, let's set up the Cloudwatch Event that triggers when an IAM Role is modified.
# Note: This will also trigger event when a role is created or deleted.
event_rule = cloudwatch.EventRule('IAMChangeEvent',
                                  event_pattern='''{
    "source": ["aws.iam"],
    "detail-type": ["AWS API Call via CloudTrail"],
    "detail": {
        "eventName": [
            "CreateRole",
            "UpdateRole",
            "DeleteRole"
        ]
    }
}\n''')

# Finally, connect this rule to the lambda function.
event_target = cloudwatch.EventTarget('IAMChangeEventTarget',
                                      rule=event_rule.name,
                                      arn=lambda_func.arn)

# Allow the Cloudwatch event to trigger the function.
lambda_perm = lambda_.Permission('IAMChangeLambdaPerm',
                                 action='lambda:InvokeFunction',
                                 function=lambda_func.name,
                                 principal='events.amazonaws.com',
                                 source_=event_rule.arn)

pulumi.export("lambda_function_name", lambda_func.name)
