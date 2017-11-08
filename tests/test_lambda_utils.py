"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

from cidr_findr.lambda_utils import parse_size, sizes_valid
import unittest

class LambdaUtilsTestCase(unittest.TestCase):
    """
    Test the lambda utils module
    """

    def test_string_integers(self):
        """
        Subnet mask passed as string
        """

        expected = [25, 24, 23]

        actual = [parse_size(size) for size in ["25", 24, "23"]]

        self.assertEqual(actual, expected)

    def test_subnet_sizes(self):
        """
        Subnet masks are too small
        """

        cases = (
            (15, False),
            (16, True),
            (17, True),
            (18, True),
            (19, True),
            (20, True),
            (21, True),
            (22, True),
            (23, True),
            (24, True),
            (25, True),
            (26, True),
            (27, True),
            (28, True),
            (29, False),
        )

        for size, expected in cases:
            self.assertEqual(sizes_valid([size]), expected)

    def test_mixed_sizes(self):
        """
        Subnet masks are too big
        """

        cases = (
            ([15, 24], False),
            ([16, 24], True),
            ([16, 29], False),
            ([15, 29], False),
        )

        for case, expected in cases:
            self.assertEqual(sizes_valid(case), expected)
