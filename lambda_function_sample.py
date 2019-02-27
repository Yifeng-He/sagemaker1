# lambda function example
'''
arn:aws:lambda:us-east-1:029716400694:function:aplusb
arn:aws:lambda:us-east-1:029716400694:function:print_results
'''
import json
import boto3
import logging
import os

MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.debug('start lambda function...')
    # get the input from s3 json file
    # TODO implement
    logger.info(event)
    s = event['A']+event['B']
    logger.info('return sum=%d' % s)
    return {'S': s
    }

