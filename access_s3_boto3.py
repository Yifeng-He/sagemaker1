# -*- coding: utf-8 -*-
"""
how to access S3 file using boto3 SDKs
references:
https://dluo.me/s3databoto3

cp and sync commands
"""

'''
# cp a file from s3 to local
aws s3 cp s3://yifenghe2019/friends.csv ./data
# cp a file from local to s3
aws s3 cp data/friends.csv s3://yifenghe2019/friends2.csv
# list files in s3
aws s3 ls s3://yifenghe2019/pk
# sync the folder (data) with s3
aws s3 sync data s3://yifenghe2019/data
# syn s3 to the local folder
aws s3 sync s3://yifenghe2019/data ./data
'''

#read csv file into pandas
import pandas as pd
bucket='yifenghe2019'
data_key = 'friends.csv'
data_location = 's3://{}/{}'.format(bucket, data_key)
df = pd.read_csv(data_location)
df.head()

# list all files in a bucket
import boto3
s3 = boto3.resource('s3')
bucket = s3.Bucket('yifenghe2019')
for obj in bucket.objects.all():
    print(obj.key)

# find an object in s3
s3_client = boto3.client('s3') #low-level functional API
obj = s3_client.get_object(Bucket='yifenghe2019', Key='data/friends.csv')
print(obj)
df_1 = pd.read_csv(obj['Body'])
df_1.head()

# find all objects in a folder in s3
files = list(bucket.objects.filter(Prefix='data/'))
for file in files:
    obj = file.get()
    content = obj['Body'].read().decode('utf-8') 
    #print(content)

# how to load a json-format file from s3 
import json
dict1={'abc': 23, 'efg': 65}
str1=json.dumps(dict1)
f=open('33.txt', 'w')
f.write(str1)
f.close()
# upload 33.txt to s3
obj = s3_client.get_object(Bucket='yifenghe2019', Key='data/33.txt')
txt = obj['Body'].read().decode('utf-8') 
dict1=json.loads(txt)

# upload a local file to s3
s3_client = boto3.client('s3')
file_name_local = 'data/44.txt'
bucket='yifenghe2019'
s3_file_path = 'data/44.txt'
s3_client.upload_file(file_name_local, bucket, s3_file_path)

# download a file from s3 to local 
import boto3
import botocore
file_name_local = 'data/4400.txt'
bucket='yifenghe2019'
s3_file_path = 'data/44.txt'
s3_resource = boto3.resource('s3')
try:
    s3_resource.Bucket(bucket).download_file(s3_file_path, file_name_local)
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("The object does not exist.")
    else:
        raise


