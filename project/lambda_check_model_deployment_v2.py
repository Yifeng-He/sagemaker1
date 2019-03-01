# lambda handler
import boto3
import logging

# logger
MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# context
sagemaker = boto3.client('sagemaker')

# function to check the status of model deployment job
def check_model_deployment(endpoint_name):
    logger.info('Polling model deployment status, endpoint name={}'.format(endpoint_name))
    # query the status of endpoint creation
    resp = sagemaker.describe_endpoint(EndpointName=endpoint_name)
    job_run_state = resp['EndpointStatus']
    job_run_error_msg = ''
    if 'FailureReason' in resp:
        job_run_error_msg = resp['FailureReason']

    logger.debug('Deployment job to endpoint: {} is currently in state: {}'.format(
            endpoint_name, job_run_state))
    
    state = 'Creating'
    if job_run_state in ['FAILED', 'OutOfService']:
        logger.debug('Deployment job to endpoint {} reported an error message of {}'.
                     format(endpoint_name, job_run_error_msg))
        state = 'Failed'
    if job_run_state == 'InService':
        state = 'InService'
    return {"State": state, "Error": job_run_error_msg}
    

# handler
def handler(event, context):
    logger.info('Handling event: {}'.format(event))
    endpoint_name = event['EndpointName']
    ret = check_model_deployment(endpoint_name)
    logger.info('Deployment job is in state: {}'.format(ret['State']))
    return ret

    