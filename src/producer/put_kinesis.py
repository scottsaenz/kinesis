import json
import os
import boto3
import uuid

def lambda_handler(event, context):
    kinesis = boto3.client('kinesis')
    stream_name = os.environ['STREAM_NAME']
    
    # Example data to send
    data = {
        'id': str(uuid.uuid4()),
        'message': 'Hello from producer!',
        'timestamp': str(context.get_remaining_time_in_millis())
    }
    
    # Put record into Kinesis stream
    response = kinesis.put_record(
        StreamName=stream_name,
        Data=json.dumps(data),
        PartitionKey=str(uuid.uuid4())
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Data sent to Kinesis',
            'sequenceNumber': response['SequenceNumber']
        })
    }
