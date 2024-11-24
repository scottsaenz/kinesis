import boto3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

def get_shard_iterators(kinesis_client, stream_name: str, start_time: datetime) -> List[str]:
    """Get shard iterators for all shards in the stream."""
    shard_iterators = []
    
    # Get all shards
    response = kinesis_client.describe_stream(StreamName=stream_name)
    shards = response['StreamDescription']['Shards']
    
    # Get iterator for each shard
    for shard in shards:
        iterator_response = kinesis_client.get_shard_iterator(
            StreamName=stream_name,
            ShardId=shard['ShardId'],
            ShardIteratorType='AT_TIMESTAMP',
            Timestamp=start_time
        )
        shard_iterators.append(iterator_response['ShardIterator'])
    
    return shard_iterators

def process_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Process individual record - customize this based on your needs."""
    try:
        # Decode and parse the data
        data = json.loads(record['Data'].decode('utf-8'))
        return {
            'data': data,
            'sequence_number': record['SequenceNumber'],
            'partition_key': record['PartitionKey'],
            'approximate_arrival_timestamp': record['ApproximateArrivalTimestamp'].isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'sequence_number': record['SequenceNumber'],
            'partition_key': record['PartitionKey']
        }

def lambda_handler(event, context):
    """
    Lambda handler to read all records from a Kinesis stream.
    
    Expected event format:
    {
        "stream_name": "your-stream-name",
        "hours_ago": 24,  # How far back to read (optional, default 24)
        "batch_size": 10000,  # Maximum number of records to return (optional, default 10000)
        "max_empty_reads": 3  # Number of empty reads before stopping (optional, default 3)
    }
    """
    try:
        # Get parameters from event or use defaults
        stream_name = event.get('stream_name') or os.environ.get('STREAM_NAME')
        if not stream_name:
            raise ValueError("Stream name not provided")
        
        hours_ago = event.get('hours_ago', 24)
        batch_size = event.get('batch_size', 10000)
        max_empty_reads = event.get('max_empty_reads', 3)

        # Initialize Kinesis client
        kinesis_client = boto3.client('kinesis')
        
        # Calculate start time
        start_time = datetime.utcnow() - timedelta(hours=hours_ago)
        
        # Get shard iterators
        shard_iterators = get_shard_iterators(kinesis_client, stream_name, start_time)
        
        all_records = []
        empty_reads = 0
        
        # Process each shard
        while shard_iterators and empty_reads < max_empty_reads and len(all_records) < batch_size:
            new_shard_iterators = []
            
            for shard_iterator in shard_iterators:
                try:
                    # Get records from shard
                    response = kinesis_client.get_records(
                        ShardIterator=shard_iterator,
                        Limit=min(10000, batch_size - len(all_records))  # Kinesis limit is 10000
                    )
                    
                    # Process records
                    if response['Records']:
                        empty_reads = 0
                        processed_records = [process_record(record) for record in response['Records']]
                        all_records.extend(processed_records)
                    else:
                        empty_reads += 1
                    
                    # Get next iterator if available
                    if response.get('NextShardIterator'):
                        new_shard_iterators.append(response['NextShardIterator'])
                        
                except kinesis_client.exceptions.ExpiredIteratorException:
                    # Handle expired iterator by getting a new one
                    continue
                except Exception as e:
                    return {
                        'statusCode': 500,
                        'body': json.dumps({
                            'error': f'Error processing shard: {str(e)}',
                            'records_processed': len(all_records)
                        })
                    }
            
            shard_iterators = new_shard_iterators
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'records_processed': len(all_records),
                'records': all_records[:batch_size],
                'truncated': len(all_records) >= batch_size,
                'start_time': start_time.isoformat()
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
