from aws_cdk import (core as cdk, aws_ec2 as ec2,
                     aws_autoscaling as asg,
                     aws_iam as iam,
                     aws_elasticloadbalancingv2 as elb,
                     aws_logs as logs)
from aws_cdk.core import Tags
import datetime

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.

# Refer: https://github.com/aws/aws-cdk/blob/master/packages/%40aws-cdk/aws-ec2/lib/instance-types.ts
m3 = ec2.InstanceClass.STANDARD3
m4 = ec2.InstanceClass.STANDARD4
m5 = ec2.InstanceClass.STANDARD5

STACK_PREFIX = 'website-search-appsec-'

class Infra(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, vpc, sg, ami_id, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Context variables can be passed from command line using -c/--context flag. The values are stored in
        # cdk.context.json file. If you do not pass any command line context key values,
        # the defaults will be picked up from cdk.context.json file
        distribution = self.node.try_get_context("distribution")
        url = self.node.try_get_context("url")
        dashboards_url = self.node.try_get_context("dashboards_url")
        keypair = self.node.try_get_context("keypair")
        if keypair == None or keypair == '':
            raise ValueError("Please provide the EC2 keypair")
        if url == None or url == '':
            raise ValueError("url cannot be null or empty")
        if dashboards_url == None or dashboards_url == '':
            raise ValueError(" dashboard_url cannot be null or empty")
        if distribution == None or distribution == '' or distribution != "tar":
            raise ValueError("Distribution cannot be null or empty. Please use tar ")

        # Creating IAM role for read only access
        ec2_iam_role = iam.Role(self, "ec2_iam_role",
                                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                                managed_policies=[
                                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess"),
                                    iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
                                ])
        stack_name = cdk.Stack.of(self).stack_name

        # Logging
        dt = datetime.datetime.utcnow()
        dtformat = dt.strftime("%m-%d-%y-t%H-%M")
        lg = logs.LogGroup(self, "LogGroup",
                           log_group_name=stack_name + '-' + dtformat,
                           retention=logs.RetentionDays.THREE_MONTHS)

        # Creating userdata for installation process
        log_group_name = lg.log_group_name
        userdata_map = {
            "common": {
                "__URL__": url,
                "__STACK_NAME__": stack_name,
                "__LG__": log_group_name
            },
            "master": {
                "__NODE_NAME__": "master-node",
                "__MASTER__": "true",
                "__DATA__": "false",
                "__INGEST__": "false"
            },
            "seed": {
                "__NODE_NAME__": "seed",
                "__MASTER__": "true",
                "__DATA__": "true",
                "__INGEST__": "false"
            },
            "data": {
                "__NODE_NAME__": "data-node",
                "__MASTER__": "false",
                "__DATA__": "true",
                "__INGEST__": "true"
            },
            "client": {
                "__NODE_NAME__": "client-node",
                "__MASTER__": "false",
                "__DATA__": "false",
                "__INGEST__": "false"
            },
            "dashboards": {
                "__DASHBOARDS_URL__": dashboards_url
            }
        }
        userdata_map["master"].update(userdata_map["common"])
        userdata_map["client"].update(userdata_map["common"])
        userdata_map["seed"].update(userdata_map["common"])
        userdata_map["data"].update(userdata_map["common"])

        with open(f"./userdata/{distribution}/main.sh") as f:
            master_userdata = cdk.Fn.sub(f.read(), userdata_map["master"])
        with open(f"./userdata/{distribution}/main.sh") as f:
            seed_userdata = cdk.Fn.sub(f.read(), userdata_map["seed"])
        with open(f"./userdata/{distribution}/main.sh") as f:
            data_userdata = cdk.Fn.sub(f.read(), userdata_map["data"])
        with open(f"./userdata/{distribution}/main.sh") as f:
            client_userdata = cdk.Fn.sub(f.read(), userdata_map["client"])
        with open(f"./userdata/{distribution}/dashboards.sh") as f:
            dashboards_userdata = cdk.Fn.sub(f.read(), userdata_map["dashboards"])

        # Launching autoscaling groups that will configure all nodes
        master_nodes = asg.AutoScalingGroup(self, "MasterASG",
                                            instance_type=ec2.InstanceType.of(m5, ec2.InstanceSize.XLARGE),
                                            machine_image=ami_id,
                                            vpc=vpc, security_group=sg,
                                            desired_capacity=2,
                                            max_capacity=2,
                                            min_capacity=2,
                                            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                                            key_name=keypair,
                                            role=ec2_iam_role,
                                            user_data=ec2.UserData.custom(master_userdata))
        Tags.of(master_nodes).add("role", "master")

        seed_node = asg.AutoScalingGroup(self, "SeedASG",
                                         instance_type=ec2.InstanceType.of(m5, ec2.InstanceSize.XLARGE),
                                         machine_image=ami_id,
                                         vpc=vpc, security_group=sg,
                                         desired_capacity=1,
                                         max_capacity=1,
                                         min_capacity=1,
                                         vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                                         key_name=keypair,
                                         role=ec2_iam_role,
                                         user_data=ec2.UserData.custom(seed_userdata))
        Tags.of(seed_node).add("role", "master")

        client_nodes = asg.AutoScalingGroup(self, "ClientASG",
                                            instance_type=ec2.InstanceType.of(m5, ec2.InstanceSize.XLARGE),
                                            machine_image=ami_id,
                                            vpc=vpc, security_group=sg,
                                            desired_capacity=2,
                                            max_capacity=2,
                                            min_capacity=2,
                                            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                            key_name=keypair,
                                            role=ec2_iam_role,
                                            user_data=ec2.UserData.custom(client_userdata + dashboards_userdata))
        Tags.of(client_nodes).add("role", "client")

        data_nodes = asg.AutoScalingGroup(self, "DataASG",
                                          instance_type=ec2.InstanceType.of(m5, ec2.InstanceSize.XLARGE),
                                          machine_image=ami_id,
                                          vpc=vpc, security_group=sg,
                                          desired_capacity=2,
                                          max_capacity=2,
                                          min_capacity=2,
                                          vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                                          key_name=keypair,
                                          role=ec2_iam_role,
                                          user_data=ec2.UserData.custom(data_userdata))
        Tags.of(data_nodes).add("role", "data")

        # creating load balancer to have a single endpoint
        self.nlb = elb.NetworkLoadBalancer(self, STACK_PREFIX + "NetworkLoadBalancer",
                                      vpc=vpc,
                                      internet_facing=False,
                                      vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE))

        opensearch_listener = self.nlb.add_listener("opensearch", port=80,
                                               protocol=elb.Protocol.TCP)
        dashboards_listener = self.nlb.add_listener("dashboards", port=5601,
                                               protocol=elb.Protocol.TCP)

        # Port mapping
        # 80 : 9200 OpenSearch
        # 5601 : 5601 OpenSearch-Dashboards
        opensearch_listener.add_targets("OpenSearchTarget",
                                        port=9200,
                                        targets=[client_nodes])
        dashboards_listener.add_targets("DashboardsTarget",
                                        port=5601,
                                        targets=[client_nodes])
        cdk.CfnOutput(self, "Load Balancer Endpoint",
                      value=self.nlb.load_balancer_dns_name)
