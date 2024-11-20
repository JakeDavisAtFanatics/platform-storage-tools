from botocore.exceptions import ClientError  # type: ignore


class AwsSsmService:
    def __init__(self, session, region):
        self.session = session
        self.region = region

    def get_parameter(self, parameter_name: str) -> str:
        try:
            ssm_client = self.session.client("ssm", region_name=self.region)
            response = ssm_client.get_parameter(
                Name=parameter_name, WithDecryption=True
            )
            return response["Parameter"]["Value"]
        except ClientError as e:
            error_message = e.response["Error"]["Message"]
            print(f"Error retrieving SSM parameter: {parameter_name} {error_message}")
            return None
