"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""


from .cidr_findr import find_next_subnet, CidrFindrException
from .lambda_utils import parse_size, send_response, sizes_valid
import boto3

ec2 = boto3.client("ec2")

def handler(event, context):
    """
    Handle a CloudFormation custom resource event
    """

    # Always return success on Delete events
    if event["RequestType"] == "Delete":
        return send_response(event, context, "SUCCESS")

    # Collect parameters
    vpc_id = event["ResourceProperties"]["VpcId"]
    sizes = event["ResourceProperties"]["Sizes"]

    sizes = tuple(map(parse_size, sizes))

    # Check the sizes are valid
    if not sizes_valid(sizes):
        return send_response(event, context, "FAILED", reason="An invalid subnet size was specified: {}".format(", ".join(map(str, sizes))))

    # Query existing subnets
    try:
        vpc_cidr = ec2.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]["CidrBlock"]
    except Exception as e:
        return send_response(event, context, "FAILED", reason=str(e))

    subnet_cidrs = [subnet["CidrBlock"] for subnet in ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]]

    # These are the CIDRs you're looking for
    try:
        result = find_next_subnet(vpc_cidr, subnet_cidrs, sizes)
    except CidrFindrException as e:
        return send_response(event, context, "FAILED", reason=str(e))

    print("VPC: {}, Subnets: {}, Request: {}, Result: {}".format(vpc_cidr, subnet_cidrs, sizes, result))

    # We have a winner
    return send_response(event, context, "SUCCESS", response_data={
        "CidrBlocks": result,
    })
