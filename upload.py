import boto3
aws_access_key_id = 'AKIAQPH4LD5O3GJVSBKP'
aws_secret_access_key = '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'

# for bucket in s3.buckets.all():
#     print(bucket.name)
with open ("https://engscoreaud.s3.us-east-2.amazonaws.com/test12.txt") as f:
    content = f.read()
    print(content)
    f.close
    # s3.upload_fileobj(f, "engscoreaud","test")
# def upload_aws(file,bucket,s3file):
#     s3 = boto3.client('s3',
#                         aws_access_key_id=aws_access_key_id,
#                         aws_secret_access_key=aws_secret_access_key)
#     s3.upload_file(file,bucket,s3file,ExtraArgs={
#         "ContentType": "txt"
#     })
#     print('uploaded')
#     return True
#
# uploaded = upload_aws('requirements.txt',"engscoreaud","test12.txt")