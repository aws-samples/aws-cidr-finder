"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

from cidr_findr import find_next_subnet
import unittest

class CidrFindrTestCase(unittest.TestCase):
    def _test_find_next_subnet(self, network=None, subnets=[], requests=[], expected=[]):
        """
        Pass the inputs to find_next_subnet
        and check they meet the expected response
        """

        actual = find_next_subnet(network, subnets, requests)

        self.assertEqual(expected, actual)

    def test_no_subnets(self):
        """
        No existing subnets
        """

        self._test_find_next_subnet(
            network="10.0.0.0/16", 
            requests=[24],
            expected=["10.0.0.0/24"],
        )

    def test_one_subnet(self):
        """
        One subnet at the beginning
        """

        self._test_find_next_subnet(
            network="10.0.0.0/16", 
            subnets=["10.0.0.0/24"],
            requests=[24],
            expected=["10.0.1.0/24"],
        )

    def test_two_adjacent_at_start(self):
        """
        Two adjacent subnets at the beginning
        """

        self._test_find_next_subnet(
            network="10.0.0.0/16",
            subnets=["10.0.0.0/24", "10.0.1.0/24"],
            requests=[24],
            expected=["10.0.2.0/24"],
        )

    def test_two_adjacent_at_start_2(self):
        """
        Two adjacent subnets at the beginning, looking for two more
        """

        self._test_find_next_subnet(
            network="10.0.0.0/16",
            subnets=["10.0.0.0/24", "10.0.1.0/24"],
            requests=[24, 24],
            expected=["10.0.2.0/24", "10.0.3.0/24"],
        )

    def test_different_sizes(self):
        """
        One subnet at the beginning, looking for two different sized subnet
        """

        self._test_find_next_subnet(
            network="10.0.0.0/16",
            subnets=["10.0.0.0/25"],
            requests=[24, 25],
            expected=["10.0.0.128/24", "10.0.1.128/25"],
        )

    def test_unordered_subnets(self):
        """
        Existing subnets not supplied in size order
        """

        self._test_find_next_subnet(
            network="172.31.0.0/16",
            subnets=["172.31.48.0/20", "172.31.0.0/20", "172.31.16.0/20", "172.31.32.0/20"],
            requests=[24],
            expected=["172.31.64.0/24"],
        )

    def test_middle_gap(self):
        """
        A subnet should fit in the gap
        """

        self._test_find_next_subnet(
            network="192.168.1.0/24",
            subnets=["192.168.1.0/26", "192.168.1.128/25"],
            requests=[26],
            expected=["192.168.1.64/26"],
        )

    def test_network_too_small(self):
        """
        Request won't fit in the network
        """

        self._test_find_next_subnet(
            network="10.0.0.0/25",
            requests=[24],
            expected=None,
        )

    def test_network_full(self):
        """
        Existing subnet fills entire network
        """

        self._test_find_next_subnet(
            network="10.0.0.0/24",
            subnets=["10.0.0.0/24"],
            requests=[24],
            expected=None,
        )

    def test_insufficient_space(self):
        """
        Subnet in the middle but not enough space either side
        """

        self._test_find_next_subnet(
            network="10.0.0.0/24",
            subnets=["10.0.0.64/25"],
            requests=[25],
            expected=None,
        )

    def test_no_requests(self):
        """
        Nothing requested
        """

        self._test_find_next_subnet(
            network="10.0.0.0/24",
            subnets=["10.0.0.0/25"],
            expected=[],
        )

    def test_gap_at_start(self):
        """
        Big enough gap at the beginning, filled after
        """

        self._test_find_next_subnet(
            network="10.0.0.0/24",
            subnets=["10.0.0.128/25"],
            requests=[25],
            expected=["10.0.0.0/25"],
        )

if __name__ == "__main__":
    unittest.main()
