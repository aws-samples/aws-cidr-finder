"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""


from . import CidrFindr, CidrFindrException
from .lambda_utils import parse_size, send_response, sizes_valid
import boto3

ec2 = boto3.client("ec2")

def handler(event, context, responder=send_response, client=ec2):
    """
    Handle a CloudFormation custom resource event
    """

    # Always return success on Delete events
    if event["RequestType"] == "Delete":
        return responder(event, context, "SUCCESS")

    properties = event.get("ResourceProperties", {})

    missing = [param for param in ("VpcId", "Sizes") if param not in properties]

    if missing:
        return responder(event, context, "FAILED", reason="Missing parameter(s): {}".format(", ".join(missing)))

    # Collect parameters
    vpc_id = properties["VpcId"]
    sizes = properties["Sizes"]

    parsed_sizes = tuple(map(parse_size, sizes))

    # Check the sizes are valid
    if not sizes_valid(parsed_sizes):
        return responder(event, context, "FAILED", reason="An invalid subnet size was specified: {}".format(", ".join(sizes)))

    # Query existing subnets
    try:
        vpc_cidr = client.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]["CidrBlock"]
    except Exception as e:
        return responder(event, context, "FAILED", reason=str(e))

    subnet_cidrs = [subnet["CidrBlock"] for subnet in client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]]

    findr = CidrFindr(vpc_cidr, subnets=subnet_cidrs)

    # These are the CIDRs you're looking for
    try:
        result = [findr.next_subnet(size) for size in sizes]
    except CidrFindrException as e:
        return responder(event, context, "FAILED", reason=str(e))

    # We have a winner
    return responder(event, context, "SUCCESS", response_data={
        "CidrBlocks": result,
    })
