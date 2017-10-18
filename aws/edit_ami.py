#!/usr/bin/python3

# Copyright (C) 2017 jamatute <jamatute@paradigmadigital.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import boto3
import argparse
import argcomplete


def load_parser(argv):
    ''' Configure environment '''
    # Argparse
    parser = argparse.ArgumentParser(
        description="Launch an instance with the AMI of an ASG")

    parser.add_argument("-l", "--list", help='List the possible ASGs',
                        action="store_true")
    parser.add_argument("-u", "--username",
                        help='Username launching the instance')
    parser.add_argument("asg_name", help='Name of the ASG', type=str, nargs="?")
    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main(argv):
    args = load_parser(argv)
    ec2a = boto3.client('autoscaling')
    ec2 = boto3.resource('ec2')

    asgs = [{'name': asg['AutoScalingGroupName'],
             'lc': asg['LaunchConfigurationName'],
             'availabilityzone': asg['AvailabilityZones'][0],
             'subnet': asg['VPCZoneIdentifier'],
             'ami': ec2a.describe_launch_configurations(
                 LaunchConfigurationNames=[asg['LaunchConfigurationName']])
             ['LaunchConfigurations'][0]['ImageId']}
            for asg in ec2a.describe_auto_scaling_groups()['AutoScalingGroups']]
    if args.list:
        print('This are the available ASGs -> AMIs')
        for asg in asgs:
            print('* {} --> {}'.format(asg['name'], asg['ami']))
        sys.exit()
    else:
        try:
            asg = [asg for asg in asgs if asg['name'] == args.asg_name][0]
        except:
            print('There is no asg with that name!')
            sys.exit(1)
        if args.username is None:
            print('You must enter your username')
            sys.exit(1)

        lc = ec2a.describe_launch_configurations(
                 LaunchConfigurationNames=[asg['lc']])
        lc = lc['LaunchConfigurations'][0]
        try:
            lc['IamInstanceProfile']
        except KeyError:
            lc['IamInstanceProfile'] = ''

        instance = ec2.create_instances(
            ImageId=lc['ImageId'],
            InstanceType='t2.micro',
            KeyName=lc['KeyName'],
            MaxCount=1,
            MinCount=1,
            IamInstanceProfile={'Name': lc['IamInstanceProfile']},
            TagSpecifications=[
                {'ResourceType': 'instance',
                 'Tags': [{'Key': 'Name',
                           'Value': 'dev-sys-edit_ami_{}'.format(
                               args.asg_name)},
                          {'Key': 'Ask',
                           'Value': args.username}]}
            ],
            Placement={'AvailabilityZone': asg['availabilityzone']},
            NetworkInterfaces=[{'DeviceIndex': 0, 'SubnetId': asg['subnet']}]
        )[0]
        print('* Launched instance {}'.format(instance.id))
        print('  Private IP: {}'.format(instance.private_ip_address))
        print('  Public IP: {}'.format(instance.public_ip_address))
        instance.security_groups.clear()
        instance.modify_attribute(Groups=lc['SecurityGroups'])
        instance.wait_until_running()
        print('\nThe instance is running :)')


if __name__ == "__main__":
    main(sys.argv)
