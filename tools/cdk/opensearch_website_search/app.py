#!/usr/bin/env python3
import os

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core, aws_ec2 as ec2

from website_search_cdk.network import Network
from website_search_cdk.infra import Infra
from website_search_cdk.api_lambda import ApiLambdaStack

STACK_PREFIX = 'website-search-appsec-'
env = core.Environment(account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
                       region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]))
app = core.App()

# Default AMI points to latest AL2
al2_ami = ec2.MachineImage.latest_amazon_linux(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                                               cpu_type=ec2.AmazonLinuxCpuType.X86_64)

network = Network(app, STACK_PREFIX + "networkstack",
                  # If you don't specify 'env', this stack will be environment-agnostic.
                  # Account/Region-dependent features and context lookups will not work,
                  # but a single synthesized template can be deployed anywhere.

                  # Uncomment the next line to specialize this stack for the AWS Account
                  # and Region that are implied by the current CLI configuration.

                  # env=core.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                  #                      region=os.getenv('CDK_DEFAULT_REGION')),

                  # Uncomment the next line if you know exactly what Account and Region you
                  # want to deploy the stack to. */

                  # env=core.Environment(account='123456789012', region='us-east-1'),

                  # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
                  env=env,
                  )
infra = Infra(app, STACK_PREFIX + "infrastack", vpc=network.vpc, sg=network.security_group,
              ami_id=al2_ami,
              env=env
              )

api_lambda = ApiLambdaStack(app, STACK_PREFIX + "apiLambdaStack", network.vpc, infra.nlb, env=env)

app.synth()
