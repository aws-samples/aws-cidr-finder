"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

def parse_size(size):
    """
    Parse the size parameter
    """
    if isinstance(size, int):
        return size

    elif isinstance(size, str) and size.isdigit():
        return int(size)

    return None

def sizes_valid(sizes):
    """
    Validate the subnet masks
    """
    return all(isinstance(size, int) and size >= 16 and size <= 28 for size in sizes)
