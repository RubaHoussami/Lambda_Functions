import json 
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table_name = 'Post'
table = dynamodb.Table(table_name)

table_name1 = 'Authentication'
table1 = dynamodb.Table(table_name1)


def lambda_handler (event, context):
    
    body = json.loads(event['body'])
    
    try:
        response1=table.query(KeyConditionExpression=Key("ID").eq(body['ID']))
        
        if 'Items' in response1 and len(response1['Items'])>0:
            
            posts=table1.scan()
            
            for post in posts['Items']:
                if body['ID'] in post['liked_posts']:
                    
                    del post['liked_posts'][post['liked_posts'].index(body['ID'])]
                    
                    table1.update_item(
                        Key={'username': post['username']},
                        UpdateExpression='SET liked_posts = :val',
                        ExpressionAttributeValues={':val': post['liked_posts']}
                    )
            
            response = table.delete_item(
                Key={
                    "ID": body['ID'],
                    "timestamp": body['timestamp']
                }
            )
            
            return {
                "statusCode" : 200,
                "headers" : {"Content-Type":"application/json"},
                "body" : json.dumps({"message" : "Post deleted!"})
            }
            
        return {
            "statusCode" : 404,
            "headers" : {"Content-Type":"application/json"},
            "body" : json.dumps({"message" : "Post does not exist!"})
        }
    
    except Exception as e:
        return {
            "statusCode" : 500,
            "headers" : {"Content-Type":"application/json"},
            "body" : json.dumps({"message" : "Internal server error!"})
        }