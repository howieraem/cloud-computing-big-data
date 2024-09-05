package com.amazonaws.samples;
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Collections;
import java.util.List;

import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Region;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.ec2.AmazonEC2;
import com.amazonaws.services.ec2.AmazonEC2ClientBuilder;
import com.amazonaws.services.ec2.model.AuthorizeSecurityGroupIngressRequest;
import com.amazonaws.services.ec2.model.CreateKeyPairRequest;
import com.amazonaws.services.ec2.model.CreateKeyPairResult;
import com.amazonaws.services.ec2.model.CreateSecurityGroupRequest;
import com.amazonaws.services.ec2.model.CreateSecurityGroupResult;
import com.amazonaws.services.ec2.model.InstanceType;
import com.amazonaws.services.ec2.model.IpPermission;
import com.amazonaws.services.ec2.model.RunInstancesRequest;
import com.amazonaws.services.ec2.model.RunInstancesResult;

public class RunEC2 {

    /*
     * Before running the code:
     *      Fill in your AWS access credentials in the provided credentials
     *      file template, and be sure to move the file to the default location
     *      (C:\\Users\\{user}\\.aws\\credentials) where the sample code will load the
     *      credentials from.
     *      https://console.aws.amazon.com/iam/home?#security_credential
     *
     * WARNING:
     *      To avoid accidental leakage of your credentials, DO NOT keep
     *      the credentials file in your source directory.
     */

    public static void main(String[] args) {

        /*
         * The ProfileCredentialsProvider will return your [default]
         * credential profile by reading from the credentials file located at
         * (C:\\Users\\{user}\\.aws\\credentials).
         */
        AWSCredentials credentials = null;
        try {
            // the credentials get filled in when you provide the secret and access keys in Eclipse toolkit 
            credentials = new ProfileCredentialsProvider("default").getCredentials();
        } catch (Exception e) {
            throw new AmazonClientException(
                    "Cannot load the credentials from the credential profiles file. " +
                    "Please make sure that your credentials file is at the correct " +
                    "location (C:\\Users\\{user}\\.aws\\credentials), and is in valid format.",
                    e);
        }

        // Create the AmazonEC2Client object so we can call various APIs.
        // We will use 'us-east-2' region
        String region = "us-east-2";
        AmazonEC2 ec2 = AmazonEC2ClientBuilder.standard()
            .withCredentials(new AWSStaticCredentialsProvider(credentials))
            .withRegion(region)
            .build();

        // Create a new security group.
        String groupName = "GettingStartedGroup";
        String groupDescription = "Getting Started Security Group";
        try {
            // Name of the group = GettingStartedGroup
            // Group Description = Getting Started Security Group
            CreateSecurityGroupRequest securityGroupRequest = new CreateSecurityGroupRequest(
                    groupName, groupDescription);
            CreateSecurityGroupResult result = ec2
                    .createSecurityGroup(securityGroupRequest);
            System.out.println(String.format("Security group created: [%s]",
                    result.getGroupId()));
        } catch (AmazonServiceException ase) {
            // Likely this means that the group is already created, so ignore.
            System.out.println(ase.getMessage());
        }

        String ipAddr = "0.0.0.0/0";

        // Get the IP of the current host, so that we can limit the Security Group
        // by default to the ip range associated with your subnet.
        try {
            InetAddress addr = InetAddress.getLocalHost();

            // Get IP Address
            ipAddr = addr.getHostAddress()+"/10";
        } catch (UnknownHostException e) {
        }

        // Create a range that you would like to populate.
        List<String> ipRanges = Collections.singletonList(ipAddr);

        // Open up port 23 for TCP traffic to the associated IP from above (e.g. ssh traffic).
        IpPermission ipPermission = new IpPermission()
                .withIpProtocol("tcp")
                .withFromPort(new Integer(22))
                .withToPort(new Integer(22))
                .withIpRanges(ipRanges);

        List<IpPermission> ipPermissions = Collections.singletonList(ipPermission);

        try {
            // Authorize the ports to the used.
            AuthorizeSecurityGroupIngressRequest ingressRequest = new AuthorizeSecurityGroupIngressRequest(
                    groupName, ipPermissions); // provide the IP permissions on our group
            ec2.authorizeSecurityGroupIngress(ingressRequest);
            System.out.println(String.format("Ingress port authroized: [%s]",
                    ipPermissions.toString()));
        } catch (AmazonServiceException ase) {
            // Ignore because this likely means the zone has already been authorized.
            System.out.println(ase.getMessage());
        }
        
        // our keyname
        String keyName = "Ec2DemoKey";
        try {
            // Creates a key-pair to connect to EC2 instance
            CreateKeyPairRequest createKeyPairRequest = new CreateKeyPairRequest();

            createKeyPairRequest.withKeyName(keyName);
            CreateKeyPairResult createKeyPairResult =
                      ec2.createKeyPair(createKeyPairRequest);
        } catch(AmazonServiceException ase) {
            System.out.println(ase.getMessage());
        }
        
        try {
            // Create a request with above details to run the image
            // get the AMI name from EC2 dashboard in AWS console
            RunInstancesRequest runInstancesRequest =
                   new RunInstancesRequest();
            runInstancesRequest.withImageId("ami-00c03f7f7f2ec15c3")
            .withInstanceType(InstanceType.T2Micro)
            .withMinCount(1)
            .withMaxCount(1)
            .withKeyName(keyName)
            .withSecurityGroups(groupName);  // provide the name of our group we created above
            
            // Run the EC2 instance
            RunInstancesResult result = ec2.runInstances(
                    runInstancesRequest);
            System.out.println("EC2 instance successfully running!");
        } catch(AmazonServiceException ase) {
            System.out.println(ase.getMessage());
        }

    }

}
