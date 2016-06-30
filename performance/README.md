# Benchmark

At present the tool, located in [performance](performance/README.md), supports the use of the following platforms:

* Microsoft's Azure
* Amazon Web Services (AWS) - specifically the EC2 platform

As this was completed over a relatively small time frame, there are still several issues with the solution.

Current issues with the tool:

* At present, there are several stages of setup that must be completed prior to being able to run this script.

## Setup

Run the install script to grab the required modules:

`python setup.py install`

If this is unsuccessful for any reason, the required modules are listed below:

`pip install boto3 azure paramiko`

### Azure

Follow the guide here [How to use Service Management from Python](https://azure.microsoft.com/en-gb/documentation/articles/cloud-services-python-how-to-use-service-management/) to create a management certificate for your Azure subscription.

The `subscription_id` and `certificate_path` must be updated in the `AzureInteraction` module, located in src/AzureInteraction.py

### AWS

There is also specific setup for Amazon's EC2 which is described here [Boto 3 Configuration](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration). As stated:
1. Authentication details must be created through the [IAM Console](https://console.aws.amazon.com/iam/home)
2. Setup can be completed by either creating necessary credential files, or through the use of the `aws configure` command with [AWS CLI](http://aws.amazon.com/cli/).


### Both Azure and AWS

There is a major setup step which is not completed automatically by the tool at present. The VM instance which is created for benchmarking, is not from a fresh image, but is in fact created by use of a pre-defined image. The image already has a default-jre installed alongside the SPECjvm2008 benchmark suite. This permits increased efficiency during test runs due to lack of requirement to install these packages post instance creation.

There is currently a function within the `AzureInteraction` module, named `capture_vm_image`. The base virtual machine must be created and installed manually, before calling this function to capture the image.

Similarly, requires the same base image to be created manually, but permits the capture of such image by use of the AWS console see [Creating an Amazon EBS-Backed Linux AMI](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/creating-an-ami-ebs.html).

The creation of a script to automate the process of creating these separate images is the main focus of the project if it is to be continued.
