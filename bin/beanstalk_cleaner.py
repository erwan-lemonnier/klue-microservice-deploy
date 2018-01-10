#!/usr/bin/env python
import click
import sys
import re
import subprocess
import logging
import json
from pprint import pprint


# Logging setup
log = logging.getLogger(__name__)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s: %(levelname)s %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


@click.command()
@click.option('--test/--no-test', help="User's new password", default=False)
@click.option('--aws-profile', help="User's password", default="klue-publish")
@click.option('--kill-oldest-instance/--no-kill-oldest-instance', help="Kill or not the oldest EC2 instance in each live environment.", default=False)
def main(test, aws_profile, kill_oldest_instance):
    """Remove swaped-out elasticbean applications and optionaly kill the oldest instance in each live environment, as a cheap
    insurance against ressource leaks.
    """

    out = subprocess.check_output("aws elasticbeanstalk describe-environments --profile %s" % aws_profile, shell=True)
    environments = json.loads(out.decode("utf-8"))

    pprint(environments)

    for env in environments['Environments']:
        application_name = env['ApplicationName']
        environment_name = env['EnvironmentName']
        version_label = env['VersionLabel']
        cname = env['CNAME']
        status = env['Status']

        log.info("Found environment %s/%s with CNAME %s" % (application_name, version_label, cname))

        if status != 'Ready':
            log.info("Environment is in status %s - Ignoring it." % status)
            continue

        if re.match('^%s-\d{6}-\d{4}-\d+\.' % application_name, cname):
            log.info("Environment is not live - Terminating it!")
            cmd = "aws elasticbeanstalk terminate-environment --environment-name %s --profile %s" % (environment_name, aws_profile)
            if test:
                log.debug("TEST MODE! would execute '%s'" % cmd)
            else:
                subprocess.check_output(cmd, shell=True)
            continue


        log.info("Environment is live - Examining its instances...")
        cmd = "aws elasticbeanstalk describe-environment-resources --environment-name %s --profile %s" % (environment_name, aws_profile)
        out = subprocess.check_output(cmd, shell=True)
        ressources = json.loads(out.decode("utf-8"))
        instances = ressources['EnvironmentResources']['Instances']
        if len(instances) < 2:
            log.info("Environment has only %s instances - Not touching them." % len(instances))
            continue


        for instance in instances:
            instance_id = instance['Id']
            cmd = "aws ec2 describe-instance-status --instance-id %s --profile %s" % (instance_id, aws_profile)
            out = subprocess.check_output(cmd, shell=True)
            status_info = json.loads(out.decode("utf-8"))
            pprint(status_info)

            if kill_oldest_instance:
                pass

            # TODO: make sure there are at least 2
            # TODO: kill the oldest running one



        log.info("Nothing to do with this environment.")


if __name__ == "__main__":
    main()
