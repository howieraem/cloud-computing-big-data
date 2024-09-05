"""Programmatically create an AWS instance, SSH to it and run commands."""
import os
# For security reasons, need to manually enter credentials
assert 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

import boto3
import requests
import time
import paramiko


KEY_PAIR_PATH = "key_pair.pem"
CREATED_INSTANCE_ADDR = ''  # leave it blank if temporary


def create_security_group(sgName, sgDesc):
    ec2 = boto3.client('ec2')
    try:
        res = ec2.create_security_group(
            GroupName=sgName,
            Description=sgDesc)
        # print('Security group created with ID', res['GroupId'])
        res2 = ec2.authorize_security_group_ingress(
            GroupId=res["GroupId"],
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ]
        )
    except:
        # already created on cloud
        pass


def createKeyPair(name):
    ec2 = boto3.resource('ec2')
    try:
        res = ec2.create_key_pair(KeyName=name)
    except:
        # already created on cloud
        return
    with open(KEY_PAIR_PATH, "w+") as file:
        file.write(res.key_material)


def createEC2(amiId, keyName, sgName, instType='t2.micro', minInst=1, maxInst=1):
    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(
        ImageId=amiId,
        MinCount=minInst,
        MaxCount=maxInst,
        InstanceType=instType,
        KeyName=keyName,
        SecurityGroups=[sgName]
    )
    
    instances[0].wait_until_running()   # wait until initialization is done
    instances[0].load()   # IMPORTANT
    return instances[0]


if __name__ == '__main__':
    if CREATED_INSTANCE_ADDR:
        instance_addr = CREATED_INSTANCE_ADDR
        instance = None  # will not terminate instance if address is given
    else:
        sgName = 'securityGroupForDemo'
        sgDesc = 'This is a security group for demo'
        keyName = 'ec2-programmatic-demo-key'
        
        # Find an appropriate (free tier eligible) amazon machine image such as here:
        # https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LaunchInstanceWizard:
        # The region must match the one defined above.
        amiId = 'ami-0a8b4cd432b1c3063'

        create_security_group(sgName, sgDesc)
        createKeyPair(keyName)
        instance = createEC2(amiId, keyName, sgName)
        instance_addr = instance.public_dns_name

    # Set up SSH
    key = paramiko.RSAKey.from_private_key_file(KEY_PAIR_PATH)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect/ssh to an instance
    client.connect(hostname=instance_addr, username="ec2-user", pkey=key)

    # Execute a command(cmd) after connecting/ssh to an instance
    try:
        while True:
            cmd = input('Input your command: ')
            stdin, stdout, stderr = client.exec_command(cmd)
            time.sleep(1)
            for line in stdout.read().decode('utf-8').split('\n'):
                print(line)
            for line in stderr.read().decode('utf-8').split('\n'):
                print(line)
    finally:
        # close the client connection once the job is done
        client.close()
        
        if not CREATED_INSTANCE_ADDR:
            # terminate instance if no existing address supplied (assuming temporary)
            instance.terminate()

