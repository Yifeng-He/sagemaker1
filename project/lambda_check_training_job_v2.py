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
sagemaker = boto3.client('glue')

# function to check the status of sagemaker training job
def check_training_job(job_name):
    logger.info('Polling training job status, job name={}'.format(job_name))
    # query the job status
    resp = sagemaker.describe_training_job(TrainingJobName=job_name)
    job_run_state = resp['TrainingJobStatus']
    job_run_error_msg = ''
    if 'FailureReason' in resp:
        job_run_error_msg = resp['FailureReason']

    logger.debug('Job with name: {} is currently in state: {}'.format(
            job_name, job_run_state))
    
    state = 'Running'
    if job_run_state in ['FAILED', 'STOPPED']:
        logger.debug('Job with name: {} reported an error message of {}'.
                     format(job_name, job_run_error_msg))
        state = 'Failed'
    if job_run_state == 'SUCCEEDED':
        state = 'Completed'
    return {"State": state, "Error": job_run_error_msg}
    

# handler
def handler(event, context):
    logger.info('Handling event: {}'.format(event))
    
    ret = check_training_job(event['JobName'])
    logger.info('Sagemaker training job is in state: {}'.format(ret['State']))
    return ret

    