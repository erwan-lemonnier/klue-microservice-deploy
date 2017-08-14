# klue-aws-toolbox

Tools to deploy a Klue micro service as a Docker container on amazon aws

## The toolbox

This toolbox contains useful tools for deploying micro-services built with
[klue-micro-service](https://github.com/erwan-lemonnier/klue-micro-service) as
Docker containers running inside amazon Beanstalk environments.

## Prerequisites

You will need:

* an amazon aws account with Beanstalk enabled
* access to a docker registry
* a Klue micro-service ready to be deployed (clone [klue-micro-service-hello-world](https://github.com/erwan-lemonnier/klue-micro-service-hello-world) to get started)

## Setup

Here are the steps you must follow before being able to deploy a Klue
micro-service to aws.

### Install Docker

```shell
apt-get install docker docker-engine
```

### Configure aws credentials

In the Amazon aws console, setup an IAM user called 'klue-publish' with the
following rights:

* AmazonEC2ReadOnlyAccess
* AWSElasticBeanstalkFullAccess
* And a custom policy with the syntax:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::config.pnt/docker/dockercfg"
            ],
            "Effect": "Allow"
        }
    ]
}
```

In a terminal on the host from where you will deploy the micro-service, configure
the aws profile of the klue-publish user:

```shell
aws configure --profile klue-publish
# Enter the credentials for backend-publish
```

### Docker registry credentials

Login into the docker registry:

```shell
docker login
```

Find the <auth-token> in ~/.docker/config.json, and upload to
S3/config.pnt/dockerconfig the following file:

```shell
{
  "https://index.docker.io/v1/": {
    "auth": "<auth-token>",
    "email": "<your-docker-login-email>"
  }
}
```

### Create an Elastic Beanstalk application for your micro-service

In the Amazon aws console, create an EBS application:
* Log into the [aws console](https://eu-west-1.console.aws.amazon.com/elasticbeanstalk)
* Go to Elastic Beanstalk console
* Click 'Create new application'
* Click 'Create web server' environment
* Environment Type: Select platform 'Generic/Docker', environment type is 'load balancing, auto scaling'
* Environment Info: set url to '<YOUR_NEW_SERVICE_NAME>'
* Configuration Details: select EC2 key pair, health check url '/ping'
* Keep all other settings to default
* Create environment!

From the root directory of your micro-service:

```shell
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
eb init --region eu-west-1 --profile klue-publish

eb list
eb use <YOUR_NEW_SERVICE_NAME>
```

## Deploy your micro-service

The default deploy pipeline for Klue micro services consists of the following
steps:
* Compile a docker image running the Klue flask server
* Run that image in a local docker engine and execute all acceptance tests against it
* If tests pass, push the docker image to a docker registry
* Create a new Elastic Beanstalk (EBS) environment in which to run your image and start it
* Run acceptance tests again, this time against the new EBS environment
* Swap this environment with the live environment of that amazon application: your service is now live!
* Run acceptance tests one last time, against the live environment

```shell
deploy_pipeline --push --deploy
```

Voila! After a few minutes your micro-service will be live, running as a docker
container in amazon Elastic Beanstalk, with all the goodies of auto-scalling
and self-repair it offers :-)

