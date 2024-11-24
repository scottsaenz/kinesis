import json
import base64

def lambda_handler(event, context):
    for record in event['Records']:
        # Decode and parse the data
        payload = base64.b64decode(record['kinesis']['data'])
        data = json.loads(payload)
        
        # Log the received data
        print(f"Received data: {data}")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed records')
    }
