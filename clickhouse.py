import pulumi
from pulumi_aws import ec2

# ClickHouse installation script
clickhouse_install_script = """#!/bin/bash
sudo apt-get update
sudo apt-get install -y apt-transport-https dirmngr
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv E0C56BD4

echo "deb http://repo.clickhouse.tech/deb/stable/ main/" | sudo tee \
    /etc/apt/sources.list.d/clickhouse.listsudo apt-get update
sudo apt-get install -y clickhouse-server clickhouse-client

sudo service clickhouse-server start
sudo clickhouse-client
"""

# Create a new security group that allows HTTP access
group = ec2.SecurityGroup('websecgrp',
    description='Connection to clickhouse',
    ingress=[
        # SSH not needed for now. We will try to mandate usage of teleport for SSH access
        ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=8123,
            to_port=8123,
            cidr_blocks=['0.0.0.0/0'], # TODO: When the infrastructure is ready, specify the subnet of the infrastructure only. Should be accessible only through VPN
        ),
    ])

# Create an EC2 instance
server = ec2.Instance('web-server-www',
    instance_type='t3a.medium',
    vpc_security_group_ids=[group.id], # reference the group object above
    user_data=clickhouse_install_script, # start-up script here
    ami="ami-085d7c5ed6c47da72" # Ubuntu 22.04 LTS
)

# Export the name of the bucket
pulumi.export('serverId', server.id)
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)
