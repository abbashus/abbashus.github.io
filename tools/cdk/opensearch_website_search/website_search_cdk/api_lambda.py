from aws_cdk import (
    core as cdk,
    aws_ec2 as ec2,
    aws_lambda as aws_lambda,
    aws_apigateway as gateway
)


class ApiLambdaStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, vpc, nlb, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        search_lambda = aws_lambda.Function(self, 'DocSearchLambda',
                                          handler='doc-search.handler',
                                          runtime=aws_lambda.Runtime.PYTHON_3_8,
                                          code=aws_lambda.Code.asset('lambda'),
                                          vpc=vpc,
                                          vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
                                          environment={
                                            'SEARCH_USER': 'admin',
                                            'SEARCH_PASS': 'admin',
                                            'NLB_ENDPOINT': nlb.load_balancer_dns_name
                                          })

        api = gateway.RestApi(self, 'ApiGatewayWithCors',
                              rest_api_name='opensearch')

        search_entity = api.root.add_resource(
            'search',
            default_cors_preflight_options=gateway.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=gateway.Cors.ALL_ORIGINS)  # TODO: only allowed origin should be opensearch.org
        )
        search_entity_lambda_integration = gateway.LambdaIntegration(
            search_lambda,
            proxy=False,
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }]
        )
        search_entity.add_method(
            'GET', search_entity_lambda_integration,
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Origin': True,
                }
            }]
        )

