"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

class Range(object):
    @staticmethod
    def ip_to_num(ip):
        ip = ip.split(".")

        num = 0

        for i in range(4):
            num = num + int(ip[3 - i]) * (256 ** i)

        return num

    @staticmethod
    def num_to_ip(num):
        ip = [0, 0, 0, 0]

        for i in range(4):
            ip[i] = str(num // (256 ** (3 - i)))
            num = num % (256 ** (3 - i))

        return ".".join(ip)

    def overlaps(self, other):
        if self.base >= other.base and self.base < other.top:
            return True

        if self.top > other.base and self.top < other.top:
            return True

        return False

    def __init__(self, base=None, top=None, size=None, cidr=None):
        if cidr:
            base, size = cidr.split("/")

        if isinstance(base, str):
            self.base = self.ip_to_num(base)
        else:
            self.base = base

        if size:
            size = int(size)

            self.top = self.base + 2 ** (32 - size)
            self.size = size
        elif top:
            if isinstance(top, str):
                self.top = self.ip_to_num(top)
            else:
                self.top = top

            self.size = math.log(self.top - self.bottom, 2)
        else:
            raise Error("Not enough information to determine IP range")

    def to_cidr(self):
        return "{}/{}".format(self.num_to_ip(self.base), self.size)

    def __str__(self):
        return self.to_cidr()

def find_next_subnet(vpc, subnets, reqs):
    vpc = Range(cidr=vpc)

    subnets.sort()

    subnets = [
        Range(cidr=subnet)
        for subnet
        in subnets
    ]

    results = []

    for req in reqs:
        attempt = Range(base=vpc.base, size=req)

        for subnet in subnets:
            # Check for clashes with subnets
            if not attempt.overlaps(subnet):
                break

            # Start at the top of the subnet we clashed with
            attempt = Range(base=subnet.top, size=req)

        # Check we have space
        if attempt.top > vpc.top:
            return None

        results.append(attempt)
        subnets.append(attempt)

    return [result.to_cidr() for result in results]
