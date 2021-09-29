import os
import smtplib
import tempfile
import boto3
from botocore import BOTOCORE_ROOT
from botocore.client import Config
from botocore.exceptions import ClientError
from io import BytesIO, StringIO
from zipfile import ZipFile, ZIP_DEFLATED


def lambda_handler(event, context):
    # Enter your aws credentials
    s3 = boto3.resource('s3',
                        aws_access_key_id='',
                        aws_secret_access_key='',
                        region_name='',
                        config=Config(signature_version='s3v4'))
# Enter S3 bucket name and folder (which lies in bucket itself) path in PREFIX_1
    bucket = ''
    PREFIX_1 = 'jet/'
    s3_client = boto3.client('s3',
                             aws_access_key_id='',
                             aws_secret_access_key='',
                             region_name='')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=PREFIX_1)

    all = response['Contents']
    files_to_zip = [str(i['Key']) for i in all[1:]]
    # we download all files to tmp directory of lambda for that we create directory structure in /tmp same as s3 files structure (subdirectory)

    for KEY in files_to_zip:
        try:
            local_file_name = '/tmp/'+KEY
            if os.path.isdir(os.path.dirname(local_file_name)):
                print(local_file_name)
            else:
                os.mkdir(os.path.dirname(local_file_name))

            s3.Bucket(bucket).download_file(KEY, local_file_name)
        except ClientError as e:
            print(e.response)

    # now create empty zip file in /tmp directory use suffix .zip if you want
    with tempfile.NamedTemporaryFile('w', suffix='.zip', delete=False) as f:
        with ZipFile(f.name, 'w', compression=ZIP_DEFLATED, allowZip64=True) as zip:
            for file in files_to_zip:
                zip.write('/tmp/'+file)

        # once zipped in temp copy it to your preferred s3 location
        # Enter the S3 'Bucket' name and 'Key' i.e. folder path, for ex. 'jet/images.zip'
    s3.meta.client.upload_file(f.name, bucket, 'jet/images.zip')
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': '',
                                                        'Key': 'jet/images.zip'},
                                                ExpiresIn=600)
    #print('All files zipped successfully!',response)
    # email the url
    SUBJECT = 'Download Link for Scraped Images'
    TO = ""  # Enter receiver's email address
    FROM = ""  # Enter sender's email address
    your_pass = ""  # Enter your password, Also turn on less secure app access in your gmail settings
    text = f"Download the images by following the link below: \n{response}"
    BODY = "\r\n".join((
        f"From : {FROM}",
        f"To: {TO}",
        f"Subject: {SUBJECT}",
        "",
        text
    ))
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    # Enter the email and password of sender
    server.login(FROM, your_pass)

    # Either use 'TO' in place of event['email'] or preferably give input in lambda function on AWS
    server.sendmail(FROM, event['email'], BODY)
    server.quit
    print("sent a link to download the images successfully")
