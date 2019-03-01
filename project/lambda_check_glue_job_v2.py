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
glue = boto3.client('glue')

# function to check the glue job
def check_glue_job(glue_job_name, glue_job_run_id):
    logger.info('Polling glue job status, job_run_id={}'.format(glue_job_run_id))
    # query glue job status
    glue_resp = glue.get_job_run(JobName=glue_job_name, RunId=glue_job_run_id,
                                 PredecessorsIncluded=False)
    job_run_state = glue_resp['JobRun']['JobRunState']
    job_run_error_msg = glue_resp['JobRun'].get('ErrorMessage', '')
    logger.debug('Job with run_id {} is currently in state: {}'.format(
            glue_job_run_id, job_run_state))
    
    state = 'Running'
    if job_run_state in ['FAILED', 'STOPPED']:
        logger.debug('Job with run_id {} reported an error message of {}'.
                     format(glue_job_run_id, job_run_error_msg))
        state = 'Failed'
    if job_run_state == 'SUCCEEDED':
        state = 'Completed'
    return {"State": state, "Error": job_run_error_msg}
    

# handler
def handler(event, context):
    logger.info('Handling event: {}'.format(event))
    
    ret = check_glue_job(event['JobName'], event['JobRunId'])
    logger.info('Glue job is in state: {}'.format(ret['State']))
    return ret
    
