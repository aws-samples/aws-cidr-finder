"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

import boto3
import json
from urllib2 import HTTPError, build_opener, HTTPHandler, Request

from cidr_findr import find_next_subnet

def send_response(event, context, response_status, reason=None, response_data={}):
    response_body = {
        "Status": response_status,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
    }

    if reason:
        response_body["Reason"] = reason

    if response_data:
        response_body["Data"] = response_data

    response_body = json.dumps(response_body)

    opener = build_opener(HTTPHandler)
    request = Request(event["ResponseURL"], data=response_body)
    request.add_header("Content-Type", "")
    request.add_header("Content-Length", len(response_body))
    request.get_method = lambda: "PUT"

    try:
        response = opener.open(request)
        print("Status code: {}".format(response.getcode()))
        print("Status message: {}".format(response.msg))
        return True
    except HTTPError as exc:
        print("Failed executing HTTP request: {}".format(exc.code))
        return False

def lambda_handler(event, context):
    """
    Handle a CloudFormation custom resource event
    """

    # Always return success on Delete events
    if event["RequestType"] == "Delete":
        return send_response(event, context, "SUCCESS")

    # Collect parameters
    vpc_id = event["ResourceProperties"]["VpcId"]
    sizes = event["ResourceProperties"]["Sizes"]

    # Check the sizes are valid
    if any(size < 16 or size > 28 for size in sizes):
        return send_response(event, context, "FAILED", reason="An invalid subnet size was specified: {}".format(", ".join(sizes)))

    # Query existing subnets
    ec2 = boto3.client("ec2")
    vpc_cidr = ec2.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]["CidrBlock"]
    subnet_cidrs = [subnet["CidrBlock"] for subnet in ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]]

    # These are the CIDRs you're looking for
    result = find_next_subnet(vpc_cidr, subnet_cidrs, sizes)

    print("VPC: {}, Subnets: {}, Request: {}, Result: {}".format(vpc_cidr, subnet_cidrs, sizes, result))

    # Nothing found
    if result is None:
        return send_response(event, context, "FAILED", reason="Not enough space for the requested CIDR blocks")

    # We have a winner
    send_response(event, context, "SUCCESS", response_data={
        "CidrBlocks": result,
    })
