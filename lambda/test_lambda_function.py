import boto3, json

lambda_client = boto3.client('lambda')

test_event = dict(plot_url="https://plot.ly/~chelsea_lyn/9008/")

lambda_client.invoke(
  FunctionName='myLambdaFunction',
  InvocationType='Event',
  Payload=json.dumps(test_event),
)