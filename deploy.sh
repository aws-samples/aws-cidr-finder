#!/bin/bash

# Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
# 
# http://aws.amazon.com/apache2.0/
# 
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

FUNCTION=cidr-findr
STACK=cidr-findr

read -p "S3 bucket (and optional prefix) to store template assets (e.g. mybucket/code): " S3PATH

bucket=${S3PATH/\/*/}
prefix=${S3PATH/#$bucket/}

if [ -n "$prefix" ]; then
    prefix=${prefix:1}
fi

# Make the zip
zip -j -9 cidr-findr.zip src/*.py

# Upload the code and template to S3
aws s3 cp cfn/cidr-findr.yaml s3://${S3PATH}/
aws s3 cp cidr-findr.zip s3://${S3PATH}/

# Create the stack
aws cloudformation create-stack --stack-name $STACK --template-url https://s3.amazonaws.com/$S3PATH/cidr-findr.yaml --parameters ParameterKey=S3Bucket,ParameterValue=$bucket ParameterKey=S3Prefix,ParameterValue=$prefix ParameterKey=FunctionName,ParameterValue=$FUNCTION --capabilities CAPABILITY_IAM
aws cloudformation wait stack-create-complete --stack-name $STACK

# Clean up
rm -f cidr-findr.zip
