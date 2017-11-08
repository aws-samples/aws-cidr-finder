"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""


from cidr_findr import find_next_subnet
from lambda_utils import parse_size, sizes_valid
from urllib.parse import urlencode
from urllib.request import urlopen, Request, HTTPError, URLError
import boto3
import json

def send_response(event, context, response_status, reason=None, response_data={}):
    body = {
        "Status": response_status,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
    }

    if reason:
        body["Reason"] = reason

    if response_data:
        body["Data"] = response_data

    print("Responding:", body)

    body = json.dumps(body).encode("utf-8")

    req = Request(event["ResponseURL"], data=body, headers={
        "Content-Length": len(body),
        "Content-Type": "",
    })
    req.get_method = lambda: "PUT"

    try:
        urlopen(req)
        return True
    except HTTPError as e:
        print("Failed executing HTTP request: {}".format(e.code))
        return False
    except URLError as e:
        print("Failed to reach the server: {}".format(e.reason))
        return False

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
    return send_response(event, context, "SUCCESS", response_data={
        "CidrBlocks": result,
    })
