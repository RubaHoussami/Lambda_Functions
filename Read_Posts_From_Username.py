import json
import boto3
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')
table_name = 'Authentication'
table = dynamodb.Table(table_name)

table_name1 = 'Post'
table1 = dynamodb.Table(table_name1)


def lambda_handler(event, context):
    
    username = event['rawQueryString'][9:]
    
    try:
        
        response = table.query(KeyConditionExpression=Key('username').eq(username))
        
        if 'Items' in response and len(response['Items']) > 0:
            
            response1 = table1.scan() 
             
            Posts=[]
            for item in response1['Items']:
                if item['username']==username:
                    Posts.append(item)
                    
            for i in range(1, len(Posts)): 
                key = Posts[i]
                j = i-1
                while j >= 0 and int(key['timestamp']) >= int(Posts[j]['timestamp']):  
                    Posts[j+1] = Posts[j]
                    j -= 1
                Posts[j+1] = key
            
            info=response['Items'][0]
            del info['password'] 
            info['Posts']=Posts
            info['Day']=str(info['Day'])
            info['Year']=str(info['Year'])
            info['avatar']=str(info['avatar'])
            
            for item in info['Posts']:
                item['likes']=str(item['likes'])
                item['comment_count']=str(item['comment_count'])
                del item['comments_dictionary']
                del item['avatar']
            
            return {
                    "statusCode" : 200,
                    "headers" : {"Content-Type" : "application/json"},
                    "body" : json.dumps(info) 
                }
                
        return {
            "statusCode" : 400,
            "headers" : {"Content-Type" : "application/json"},
            "body" : json.dumps({'message' : "User not found!"}) 
        }
            
    except Exception as e:
        return {
            "statusCode" : 500, # internal server error - failure
            "headers" : {"Content-Type":"application/json"},
            "body" : json.dumps({"message" : "Internal server error! "}) 
        }