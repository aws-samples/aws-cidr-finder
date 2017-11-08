"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

#import cidr_findr
from cidr_findr import lambda_utils
import cidr_findr.lambda_handler
from cidr_findr.lambda_handler import handler
import unittest

class MockEc2():
    def describe_vpcs(self, **kwargs):
        return {
            "Vpcs": [
                {
                    "CidrBlock": "10.0.0.0/16",
                },
            ],
        }

    def describe_subnets(self, **kwargs):
        return {
            "Subnets": [
                {
                    "CidrBlock": "10.0.0.0/24",
                },
                {
                    "CidrBlock": "10.0.0.0/25",
                },
            ]
        }

class LambdaHandlerTestCase(unittest.TestCase):
    """
    Test the lambda handler function
    """

    def __responder(self, event, context, status, reason=None, response_data={}):
        self.response = {
            "status": status,
            "reason": reason,
            "data": response_data,
        }

    def test_delete(self):
        expected = {
            "status": "SUCCESS",
            "reason": None,
            "data": {},
        }

        handler({"RequestType": "Delete"}, {}, responder=self.__responder)

        self.assertEqual(self.response, expected)

    def test_missing_vpcid(self):
        expected = {
            "status": "FAILED",
            "reason": "Missing parameter(s): VpcId",
            "data": {},
        }

        request = {
            "RequestType": "Create",
            "ResourceProperties": {
                "Sizes": "",
            },
        }

        handler(request, {}, responder=self.__responder)

        self.assertEqual(self.response, expected)

    def test_missing_sizes(self):
        expected = {
            "status": "FAILED",
            "reason": "Missing parameter(s): Sizes",
            "data": {},
        }

        request = {
            "RequestType": "Create",
            "ResourceProperties": {
                "VpcId": "",
            },
        }

        handler(request, {}, responder=self.__responder)

        self.assertEqual(self.response, expected)

    def test_missing_both(self):
        expected = {
            "status": "FAILED",
            "reason": "Missing parameter(s): VpcId, Sizes",
            "data": {},
        }

        request = {
            "RequestType": "Create",
            "ResourceProperties": {
            },
        }

        handler(request, {}, responder=self.__responder)

        self.assertEqual(self.response, expected)

    def test_bad_sizes(self):
        expected = {
            "status": "FAILED",
            "reason": "An invalid subnet size was specified: 23, camel, 25",
            "data": {},
        }

        request = {
            "RequestType": "Create",
            "ResourceProperties": {
                "VpcId": "",
                "Sizes": ["23", "camel", "25"],
            },
        }

        handler(request, {}, responder=self.__responder)

        self.assertEqual(self.response, expected)

    def test_request_too_large(self):
        expected = {
            "status": "FAILED",
            "reason": "Not enough space for the requested CIDR blocks",
            "data": {},
        }

        request = {
            "RequestType": "Create",
            "ResourceProperties": {
                "VpcId": "",
                "Sizes": ["16"],
            },
        }

        handler(request, {}, responder=self.__responder, client=MockEc2())

        self.assertEqual(self.response, expected)

    def test_success(self):
        expected = {
            "status": "SUCCESS",
            "reason": None,
            "data": {
                "CidrBlocks": ["10.0.1.0/17"],
            },
        }

        request = {
            "RequestType": "Create",
            "ResourceProperties": {
                "VpcId": "",
                "Sizes": ["17"],
            },
        }

        handler(request, {}, responder=self.__responder, client=MockEc2())

        self.assertEqual(self.response, expected)
