import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# S3://EUREX-PDS/2018-08-15
SOURCE_S3_URI = 's3://project-stock-raw'
dyframe = glueContext.create_dynamic_frame_from_options('s3', connection_options={
        'paths':[SOURCE_S3_URI]
        },
        format='csv',
        format_options={'withHeader': True})

# convert to spark dataframe
#df_spark = dyframe.toDF()

# WRITE THE DATA TO THE TARGET BUCKET
glueContext.write_dynamic_frame.from_options(frame = dyframe,
              connection_type = "s3",
              connection_options = {"path": "s3://project-stock-processed/pk2"},
              format = "parquet")

job.commit()
