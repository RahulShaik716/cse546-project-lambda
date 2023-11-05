import json
import boto3

aws_secret = "AKIAV5DKHYESZAO7ZVGM"
aws_secret_key = "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"
def upload_items():
    with open('student_data.json', 'r') as datafile:
        records = json.load(datafile)

    dynamodb = boto3.resource('dynamodb', region_name='us-west-1',aws_access_key_id=aws_secret,aws_secret_access_key=aws_secret_key)
    student_table = dynamodb.Table('mgstudentable')

    for record in records:
        student_table.put_item(Item=record)

def get_item():
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1',aws_access_key_id=aws_secret,aws_secret_access_key=aws_secret_key)
    student_table = dynamodb.Table('mgstudentable')
    item = student_table.get_item(Key={'name':'mr_bean'})['Item']
    print(item)
    print(f"{item['name']},{item['major']},{item['year']}")

upload_items()
get_item()