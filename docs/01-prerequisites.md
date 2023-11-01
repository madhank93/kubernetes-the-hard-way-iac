# Prerequisites

## Amazon Web Services

This tutorial leverages the [Amazon Web Services](https://aws.amazon.com/) to streamline provisioning of the compute infrastructure required to bootstrap a Kubernetes cluster from the ground up. It would cost less then $2 for a 24 hour period that would take to complete this exercise.

> The compute resources required for this tutorial exceed the Amazon Web Services free tier. Make sure that you clean up the resource at the end of the activity to avoid incurring unwanted costs. 

## Amazon Web Services CLI

### Install the AWS CLI

Follow the AWS CLI [documentation](https://aws.amazon.com/cli/) to install and configure the `aws` command line utility.

Verify the AWS CLI version using:

```
aws --version
```

### Set a Default Compute Region and Zone

This tutorial assumes a default compute region and zone have been configured.

Go ahead and set a default compute region:

```
AWS_REGION=us-west-1

aws configure set default.region $AWS_REGION
```


## Pulumi installation

### Install the Pulumi CLI

Follow the Pulumi installation [documentation](https://www.pulumi.com/docs/install/) to install and configure the `pulumi` CLI 

```sh
curl -fsSL https://get.pulumi.com | sh
```

Verify the Pulumi version by running the following command

```sh
pulumi version
```

### Getting started with Pulumi & AWS

Refer the Pulumi environment setup [guide](https://www.pulumi.com/docs/clouds/aws/get-started/begin/) and language run-time & project creation [documentation](https://www.pulumi.com/docs/clouds/aws/get-started/create-project/)


## Ansible installation

Follow the Ansible installation [documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) to install ansible.

Verify the Ansible version by running the following command

```sh
ansible --version
```

Next: [Provisioning Compute Resources](02-compute-resources.md)