# lambda handler
import boto3
import logging
from time import gmtime, strftime
import os
from sagemaker.amazon.amazon_estimator import get_image_uri
from sagemaker import get_execution_role

# logger
MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# context
sagemaker = boto3.client('sagemaker')
role_arn = get_execution_role()

# function to start the sagemaker training job
def start_training_job(role_arn, s3_train_uri, s3_validation_uri, 
                       s3_output_uri, feature_count):
    
    job_name = 'model-train-{}'.format(strftime('%Y-%m-%d-%H-%M-%S', gmtime()))
    logger.info('Starting sagemaker training job named {}'.format(job_name))
    
    container = get_image_uri(boto3.Session().region_name, 'linear-learner')

    #alternative way: 1) use sagemaker notebook to do model training, 2) use
    #use boto3 to get the job parameters to train the model periodically
    training_params = {
            'TrainingJobName': job_name,
            
            'AlgorithmSpecification': {
                'TrainingImage': container,
                'TrainingInputMode': 'File',
            },
                    
            'RoleArn': role_arn,
            
            'OutputDataConfig': {
                'S3OutputPath': s3_output_uri
            },
                    
            'ResourceConfig': {
                'InstanceType': 'ml.m4.4xlarge',
                'InstanceCount': 1,
                'VolumeSizeInGB': 100,
            },
                    
            'HyperParameters': {
                'feature_dim': feature_count,
                'predictor_type': 'regressor',
                'epochs': '100'
            },
                    
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 3600
            },
                    
            'InputDataConfig': [
                # train channel
                {
                    'ChannelName': 'train',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': s3_train_uri,
                            'S3DataDistributionType': 'FullyReplicated'
                        }
                    },
                    'ContentType': 'text/csv',
                    'CompressionType': 'None'
                },
                #validation channel
                {
                    'ChannelName': 'validation',
                    'DataSource': {
                        'S3DataSource': {
                            'S3DataType': 'S3Prefix',
                            'S3Uri': s3_validation_uri,
                            'S3DataDistributionType': 'FullyReplicated'
                        }
                    },
                    'ContentType': 'text/csv',
                    'CompressionType': 'None'
                }                       
            ]  
            
        }
    
    # running sagemaker training job
    logger.info('Running sagemaker training job named: {}'.format(job_name))
    response = sagemaker.create_training_job(**training_params)
    training_job_arn = response['TrainingJobArn']
    #status = sagemaker.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
    return {'TrainingJobName': job_name, 'TrainingJobArn': training_job_arn, 'Container': container}

    
# handler
def handler(event, context):
    logger.info('Handling event: {}'.format(event))
    
    DATA_LAKE_BUCKET = event['TARGET_BUCKET']
    s3_train_uri = 's3://{}/ml/data/train'.format(DATA_LAKE_BUCKET)
    s3_validation_uri = 's3://{}/ml/data/validation'.format(DATA_LAKE_BUCKET)
    s3_output_uri = 's3://{}/ml/model/output'.format(DATA_LAKE_BUCKET)
    feature_count = event['FeatureCount']

    dict_job_info = start_training_job(role_arn, s3_train_uri, s3_validation_uri, 
                       s3_output_uri, feature_count)
    logger.info('Starting sagemaker training job with job_name={} and job_arn={}'.
                format(dict_job_info['TrainingJobName'], dict_job_info['TrainingJobArn']))
    return dict_job_info
  
    