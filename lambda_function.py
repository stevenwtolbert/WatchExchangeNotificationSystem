import json
import praw
import boto3
import base64
from botocore.exceptions import ClientError 

def get_secret():
    secret_name = "API_KEY"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            raise e
            
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret  = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)
                     
def put_id(uid, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('watchexchange_uid_table')
    response = table.put_item(Item={'uid': uid},ConditionExpression = "attribute_not_exists(id)")
    return response
    
def lambda_handler(event, context):
    new_item_found = False
    client = boto3.client('sns')
    reddit_api_keys = get_secret()
    
    reddit = praw.Reddit(client_id=reddit_api_keys['REDDIT_CLIENT_ID'],
                         client_secret=reddit_api_keys['REDDIT_CLIENT_SECRET'],
                         user_agent="watchexchange_notification_system:v1 (by u/Gandor)")
    
    posts = {"Title" : [],
             "Link"  : [],
             "Price" : []}
             
    keywords = ['rolex', 'omega', 'patek', 'audemars', 'lange', 'vacheron']
    
    for submission in reddit.subreddit("watchexchange").new(limit=15):
        prices_found = []
        if(any(substring in submission.title.lower() for substring in keywords)):
            uid = submission.id
            try:
                put_id(uid)
            except: 
                print("{} ID Already Exists in Database".format(uid))
                continue
            print("NEW ENTRY {}".format(uid))
            new_item_found = True

            title = submission.title
            link = "reddit.com{}".format(submission.permalink)
            seller = submission.author
            comments = submission.comments
            for comment in comments:
                if(comment.author == seller):
                    detail_substrings = comment.body.split(" ")
                    for substring in detail_substrings:
                        if("$" in substring):
                            prices_found.append(substring)

            posts['Title'].append(title)
            posts['Link'].append(link)
            posts['Price'].append(prices_found)
         
    message = {"Title": posts['Title'],
               "Link" : posts['Link'],
               "Price": posts['Price']}
    if(new_item_found == True):        
        response = client.publish(TargetArn=reddit_api_keys['REDDIT_SNS_ARN'],
                                  Message=json.dumps({'default': json.dumps(message)}),
                                  MessageStructure='json')
                              
    return {
        'statusCode': 200,
    }
