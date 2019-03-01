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

# function to start the glue job
def start_glue_job(glue_job_name, glue_job_args):
    logger.info('Starting glue job named {}'.format(glue_job_name))
    response = glue.start_job_run(JobName=glue_job_name, Arguments=glue_job_args)
    glue_job_run_id = response['JobRunId']
    return glue_job_run_id
    

# handler
def handler(event, context):
    logger.info('Handling event: {}'.format(event))
    job_name = event['JobName']
    job_parameters = {}
    if 'JobParameters' in event:
        job_parameters = event['JobParameters']
    job_id = start_glue_job(job_name, job_parameters)
    logger.info('Starting glue job with job ID: {}'.format(job_id))
    return job_id
    