import boto3

lambda_client = boto3.client('lambda')

with open('lambda.zip', 'rb') as f:
  zipped_code = f.read()

lambda_client.update_function_code(
  FunctionName='myLambdaFunction',
  ZipFile=zipped_code,
)