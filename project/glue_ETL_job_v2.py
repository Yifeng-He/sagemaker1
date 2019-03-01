import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import Window
import pyspark.sql.functions as F
from pyspark.ml.feature import StringIndexer
import logging

# logger
MSG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=MSG_FORMAT, datefmt=DATETIME_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

## parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'SOURCE_BUCKET', 'TARGET_BUCKET','CRAWLER'])
INPUT_S3_URI = 'S3://{}/{}'.format(args['SOURCE_BUCKET'])
DATA_LAKE_BUCKET = args['TARGET_BUCKET']
OUTPUT_S3_RAW_URI = 's3://{}/raw/'.format(DATA_LAKE_BUCKET)
OUTPUT_S3_ML_URI = 's3://{}/ml/data'.format(DATA_LAKE_BUCKET)

CRAWLER = args['CRAWLER']

# context
s3 = boto3.client('s3')
glue = boto3.client('glue', region_name='us-east-1')
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

############# step 1:  copy data into the data lake ###################
logger.info('Copying data from {} to {}'.format(INPUT_S3_URI, OUTPUT_S3_RAW_URI))
# load the data from the source into dynamic frame
dyframe = glueContext.create_dynamic_frame_from_options(
        connection_type ='s3', 
        connection_options={'paths':[INPUT_S3_URI]},
        format='csv',
        format_options={'withHeader': True})
# copy the raw data into data lake in parquet format
if dyframe.count() > 0:
    glueContext.write_dynamic_frame.from_options(
            frame = dyframe,
            connection_type = "s3",
            connection_options = {"path": "s3://project-stock-processed/pk2"},
            format = "parquet")
else:
    logger.debug('Input s3 URI contains no data, skipping')
logger.info('Completed copying data from the source bucket to the data lake')


############# step 2:  feature engineering ###################
STRING_COLS = ['marketsegment', 'isin', 'securitytype']
NUM_COLS = ['startprice', 'maxprice', 'minprice', 'endprice', 
            'numberofcontracts', 'numberoftrades']
DATE_COLS = ['date', 'time']
FEATURE_COLS = STRING_COLS + NUM_COLS + DATE_COLS

# convert the dynamic frame to spark dataframe
feature_df = dyframe.toDF().select(FEATURE_COLS)
feature_df = feature_df.withColumn('pct_change', (feature_df.maxprice - 
                                    feature_df.minprice)/feature_df.endprice)
feature_df = feature_df.withColumn('gmt_datetime', F.to_utc_timestamp(
        F.concat(F.date_format(feature_df.date), F.date_format(feature_df.time))))

window = Window.partitionBy('isin').orderBy('gmt_datetime')
feature_df = feature_df.withColumn('next_pct_change', 
                                   F.lead(feature_df.pct_change).over(window))
# label encoding for string cols
for col in STRING_COLS:
    label_encoder = StringIndexer(inputCol=col, outputCol='{}_category'.format(col))
    label_encoder = label_encoder.fit(feature_df)
    feature_df = label_encoder.transform(feature_df)
feature_df = feature_df.select(['next_pct_change', 'pct_change']+
                               NUM_COLS+['{}_category'.format(s) for s in STRING_COLS])
# data split
train_df, valid_df, test_df = feature_df.random_split([0.6, 0.2, 0.2])
logger.info('Completed feature engineering')


############# step 3:  upload train/val/test data to S3 ###################
train_df.coaleace(100).write.mode('overwrite').csv(OUTPUT_S3_ML_URI+'/train', header=True)
valid_df.coaleace(100).write.mode('overwrite').csv(OUTPUT_S3_ML_URI+'/validation', header=True)
test_df.coaleace(100).write.mode('overwrite').csv(OUTPUT_S3_ML_URI+'/test', header=True)
logger.info('Completed uploaded train/validation/test data sets to s3')

## running crawler to craw the data in the data lake
logger.info('Starting to crawl the data in the data lake with crawler: {}'.format(CRAWLER))
glue.start_crawler(CRAWLER)

job.commit()
logger.info('Completed data transformation')
