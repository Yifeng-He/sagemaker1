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
    
    # form the arguments for glue job from state inputs
    job_name = event['GlueJobName']
    glue_params = {
            '--JOB_NAME': job_name,
            '--SOURCE_BUCKET': event['SourceBucket'], 
            '--TARGET_BUCKET': event['TargetBucket'],
            '--CRAWLER': event['Crawler']
        }  

    dict_job_run_id = start_glue_job(job_name, glue_params)
    job_run_id = dict_job_run_id['JobRunId']
    logger.info('Starting glue job with job ID: {}'.format(job_run_id))
    return job_run_id
    
