# klue-aws-toolbox

Tools to deploy a Klue micro service as a Docker container on amazon Elastic Beanstalk.

## The toolbox

This is a collection of tools for deploying micro-services built with
[klue-micro-service](https://github.com/erwan-lemonnier/klue-micro-service) as
Docker containers running inside amazon Elastic Beanstalk environments.

## Prerequisites

You will need:

* An amazon aws account with Beanstalk enabled
* Access to a docker registry (like [hub.docker.com](https://hub.docker.com/))
* A Klue micro-service ready to be deployed (clone [klue-micro-service-hello-world](https://github.com/erwan-lemonnier/klue-micro-service-hello-world) to get started)

## Setup

Here are the steps you must follow before being able to deploy a Klue
micro-service to aws.

### Install Docker

You need to be able to run a docker container locally on your development host,
as part of the deployment pipeline for Klue micro-services. Simply install
docker engine as follows:

```shell
apt-get install docker docker-engine
```

### Create a S3 bucket for docker config

Beanstalk's way of receiving the docker configuration for an image relies on a
S3 bucket to pass the configuration.

In the amazon aws console, create a S3 bucket named 'klue-config'. In it,
create an empty directory called 'docker'.

### Docker registry credentials

Here we assume that you are using hub.docker.com as your image repository.

From a terminal, login into docker hub:

```shell
docker login
```

Find the <auth-token> in ~/.docker/config.json, and upload to
'S3/klue-config/docker/dockercfg' the following file:

```shell
{
  "https://index.docker.io/v1/": {
    "auth": "<auth-token>",
    "email": "<your-docker-login-email>"
  }
}
```

With that, amazon will know how to fetch your micro-service image from the
docker registry.

### Configure aws credentials

In the Amazon aws console, setup an IAM user called 'klue-publish' with the
following rights:

* AmazonEC2ReadOnlyAccess
* AWSElasticBeanstalkFullAccess
* And a custom policy giving this user access to the 'klue-config' S3 bucket:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::klue-config/docker/dockercfg"
            ],
            "Effect": "Allow"
        }
    ]
}
```

Still in the aws console, create an access key for the user 'klue-publish' and
note its 'Access key ID' and 'Secret access key'.

Then, in a terminal on the host from where you will deploy the micro-service,
configure the aws profile of the klue-publish user:

```shell
aws configure --profile klue-publish
# Enter the 'Access key ID' and 'Secret access key' for klue-publish
# Choose the default region that suits you (ex: eu-west-1)
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

Calling 'eb use' marks this beanstalk application as the current live instance
of the micro-service, that will be swapped with the new instance upon every
deploy.

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

## Manual removal of out-dated Beanstalk environment

WARNING! The deploy pipeline does not remove the old application environment
after swapping it away in favor of a new one. The old environment is kept so
that you may swap it back into live position should your new environment be
failing despite all acceptance tests.

Each environment consumes resources in terms of instance time and load
balancer: you should therefore regularly manually delete old environments from
your Beanstalk application.
