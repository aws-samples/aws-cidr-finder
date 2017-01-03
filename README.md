# CIDR finder

AWS CIDR Finder is a tool for adding more convenience to your [AWS CloudFormation](https://aws.amazon.com/cloudformation/) templates and [AWS Service Catalog](https://aws.amazon.com/servicecatalog/) products by calculating the [CIDR ranges](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Subnets.html) of new subnets for you so that your users don't have to supply them.

In the DevOps world, where automation rules, the exact IP addresses of your servers don't really matter when they can otherwise be identified by [tagging](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_Tags.html) or [API](http://docs.aws.amazon.com/AWSEC2/latest/APIReference/Welcome.html) calls. For that reason, when launching CloudFormation stacks, it's good to have an option not to have to specify the CIDR ranges for your subnets.

AWS CIDR finder provides a Lambda function that can be used as a [custom resource](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources.html) within your own CloudFormation templates to calculate CIDR ranges.

## Usage

First of all, you need to install AWS CIDR finder in your account. The included `deploy.sh` script will create the lambda function for you and provide an [exported CloudFormation value](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-exports.html) that you can [make use of](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html) in your own templates.

### Example CloudFormation template

The following example is included in full in the `cfn` directory and creates a new VPC along with 3 new subnets using automatically calculated CIDR ranges.

```yaml
Resources:
  # Create a new VPC for the example
  Vpc:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 192.168.0.0/23

  # Call the custom resource, specify 3 subnets of different sizes.
  # The resource will have a property called CidrBlocks with an array of 3 CIDR block definitions
  CidrFindr:
    Type: Custom::CidrFindr
    Properties:
      ServiceToken: !ImportValue CidrFindr
      VpcId: !Ref Vpc  # Refer to the VPC created above
      Sizes: [24, 25, 26]  # 3 subnets of differing sizes

  # Use the first entry from CidrFindr's CidrBlocks property
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      CidrBlock: !Select [0, !GetAtt [CidrFindr, CidrBlocks]]
      VpcId: !Ref Vpc
      
  # Use the second entry from CidrFindr's CidrBlocks property
  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      CidrBlock: !Select [1, !GetAtt [CidrFindr, CidrBlocks]]
      VpcId: !Ref Vpc
      
  # Use the third entry from CidrFindr's CidrBlocks property
  Subnet3:
    Type: AWS::EC2::Subnet
    Properties:
      CidrBlock: !Select [2, !GetAtt [CidrFindr, CidrBlocks]]
      VpcId: !Ref Vpc
```
