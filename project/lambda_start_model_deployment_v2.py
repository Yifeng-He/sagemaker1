# lambda handler
import boto3
import logging
from time import gmtime, strftime
from sagemaker import get_execution_role

# logger
MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# context
sagemaker = boto3.client('sagemaker')
role = get_execution_role()

# function to start endpoint deployment
def start_model_deployment(job_name, container):
    logger.info('Deploying the model onto an inference endpoint')

    # step 1: create model
    model_name = job_name + '-model' 
    info = sagemaker.describe_training_job(TrainingJobName=job_name)
    model_url = info['ModelArtifacts']['S3ModelArtifacts']   
    primary_container = {
        'Image': container,
        'ModelDataUrl': model_url
    }
    create_model_response = sagemaker.create_model(
        ModelName = model_name,
        ExecutionRoleArn = role,
        PrimaryContainer = primary_container)
    model_arn = create_model_response['ModelArn']
    
    # step 2: set up endpoint configuration
    endpoint_config_name = 'EndpointConfig-' + job_name + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    create_endpoint_config_response = sagemaker.create_endpoint_config(
        EndpointConfigName = endpoint_config_name,
        ProductionVariants=[{
            'InstanceType':'ml.m4.xlarge',
            'InitialVariantWeight':1,
            'InitialInstanceCount':1,
            'ModelName':model_name,
            'VariantName':'AllTraffic'}])
    endpointconfig_arn = create_endpoint_config_response['EndpointConfigArn']
    
    # step 3: start to create the inference endpoint
    endpoint_name = 'Endpoint-' + job_name +  strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    create_endpoint_response = sagemaker.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name)
    endpoint_arn = create_endpoint_response['EndpointArn']
    logger.info('Inference endpoint is being created, endpoint name = {}, endpoint ARN = {}'.
                format(endpoint_name, endpoint_arn))
    
    return {'EndpointName': endpoint_name, 'EndpointArn': endpoint_arn}


# handler
def handler(event, context):
    logger.info('Handling event: {}'.format(event))
    container = event['TrainingJobInfo']['Container']
    job_name = event['TrainingJobInfo']['TrainingJobName']
    endpoint_info = start_model_deployment(job_name, container)
    return endpoint_info

    