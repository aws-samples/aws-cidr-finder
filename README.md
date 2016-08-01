# CIDR finder

This is a custom CloudFormation resource intended to be used in situations where you wish to create new subnets but don't wish to have to manually specify their CIDR ranges.

For example, you could use this with Service Catalog to allow a team to self-provision a new subnet and have it automatically choose the next available CIDR block.

The custom resource will return CIDR notation that corresponds to the next available block of the size requested.

## Usage

The best way to demonstrate usage is by example. See `cfn/example-success.yaml` for an example CloudFormation template that creates a new VPC and adds three new subnets to it - generating the subnets' ranges automatically.

The template in `cfn/example-failure.yaml` provides an example of what happens when the subnets of the requested sizes aren't available.

## Installing

There is a script included (`deploy.sh`) that will zip the lambda source code and store it, along with a CloudFormation template in an S3 bucket and location that you specify. Once uploaded, the script then deploys the CloudFormation stack which results in an exported value named `CidrFindr` which can be used as a custom resource in your templates as in the example templates included in the `cfn` folder.
