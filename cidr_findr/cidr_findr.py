"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

class CidrFindrException(Exception):
    pass

class Range(object):
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
            raise CidrFindrException("Not enough information to determine IP range")

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
        if self.top > other.base and self.top < other.top:
            return True

        if self.base >= other.base and self.base < other.top:
            return True

        if other.top > self.base and other.top < self.top:
            return True

        if other.base >= self.base and other.base < self.top:
            return True

        return False

    def to_cidr(self):
        return "{}/{}".format(self.num_to_ip(self.base), self.size)

    def __str__(self):
        return self.to_cidr()

class Network():
    def __init__(self, network, subnets):
        self.network = network
        self.subnets = subnets

    def next_subnet(self, req):
        if req <= self.network.size:
            raise CidrFindrException("Can't fit a /{} subnet in a /{} network".format(req, self.network.size))

        for base in range(self.network.base, self.network.top, 2 ** (32 - req)):
            attempt = Range(base=base, size=req)

            if attempt.top > self.network.top:
                break

            if not any(attempt.overlaps(subnet) for subnet in self.subnets):
                self.subnets.append(attempt)
                return attempt.to_cidr()

        raise CidrFindrException("Not enough space for a /{} in {}".format(req, self.network.to_cidr()))

class CidrFindr():
    def __init__(self, network=None, networks=[], subnets=[]):
        if network:
            networks = [network]

        networks = [Range(cidr=network) for network in sorted(networks)]

        subnets = [
            Range(cidr=subnet)
            for subnet
            in sorted(subnets)
        ]

        self.networks = [
            Network(network, [subnet for subnet in subnets if subnet.overlaps(network)])
            for network in networks
        ]

    def next_subnet(self, req):
        for network in self.networks:
            try:
                return network.next_subnet(req)
            except CidrFindrException:
                pass

        raise CidrFindrException("Not enough space for the requested CIDR blocks")
