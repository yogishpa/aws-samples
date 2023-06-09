import json
import boto3
import urllib.request
from botocore.config import Config

my_config = Config(
    region_name = 'us-east-1',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

#define the function
def lambda_handler(event, context):
    #define the elasticbeastalk client
    client = boto3.client('elasticbeanstalk',config=my_config)
    #define the response
    response = client.describe_environments()
    #define the list of running instances
    running_instances = []
    
    #define the list of running environments
    running_environments = []

    #iterate through the list of environments

    for environment in response['Environments']:
        #if the environment is running
        if environment['Status'] == 'Ready':

            #add the environment id to the list
            running_environments.append(environment['EnvironmentId'])
            
            #define list for running instances in the environment
            running_instances = []
            
            #iterate through the list of environment and print the instance Ids
            for environment in running_environments:

                eb_instance_list_respose = client.describe_environment_resources(EnvironmentId=environment)

                for eb_instances in eb_instance_list_respose['EnvironmentResources']['Instances']:
                #add running instance to the list
                    running_instances.append(eb_instances.get('Id'))
                    #define the ssm client
                    ssm_client = boto3.client('ssm')
                    #define the ssm send-command for sending powershell commands
                    ssm_response = ssm_client.send_command(
                        InstanceIds = [eb_instances.get('Id')],
                        DocumentName = 'AWS-RunPowerShellScript',
                        Parameters = {
                            'commands': ["Read-S3Object -BucketName sampledatabucket -KeyPrefix Test -Folder C:\SampleFiles"]
                    }

                )