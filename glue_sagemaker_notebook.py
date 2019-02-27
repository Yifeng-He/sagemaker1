# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 20:09:49 2019

@author: yifeng
"""

# glue sagemaker notebook

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

glueContext = GlueContext(SparkContext.getOrCreate())
#SparkSession available as 'spark'.

# read csv from a s3 folder
SOURCE_S3_URI = 's3://project-stock-raw'
dyframe = glueContext.create_dynamic_frame_from_options('s3', connection_options={
        'paths':[SOURCE_S3_URI]
        },
        format='csv',
        format_options={'withHeader': True})
# convert to a spark dataframe
df_spark = dyframe.toDF()
#df_spark.show()

# save the data into another s3 folder in parquet format
glueContext.write_dynamic_frame.from_options(frame = dyframe,
              connection_type = "s3",
              connection_options = {"path": "s3://project-stock-processed/pk"},
              format = "parquet")

# load the data into dataframe using pyspark 
# the s3 contain many csv files, pyspark load all csv files into a dataframe
df2=spark.read.options(header=True, inferSchema=True).csv('s3://project-stock-raw')
df2.show()
