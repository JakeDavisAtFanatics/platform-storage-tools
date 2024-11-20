from botocore.exceptions import ClientError  # type: ignore


class AwsRdsService:
    def __init__(self, session):
        self.session = session

    def get_rds_instance(self, environment_name: str, region: str):
        try:
            rds_client = self.session.client("rds", region_name=region)
            instance_name = f"{environment_name}-postgresql"
            response = rds_client.describe_db_instances(
                DBInstanceIdentifier=instance_name
            )

            if response["DBInstances"]:
                instance = response["DBInstances"][0]
                result = {
                    "primary": {
                        "endpoint": instance["Endpoint"]["Address"],
                        "instance_name": instance_name,
                    }
                }

                # Check for read replicas
                for replica in instance.get("ReadReplicaDBInstanceIdentifiers", []):
                    replica_response = rds_client.describe_db_instances(
                        DBInstanceIdentifier=replica
                    )
                    if replica_response["DBInstances"]:
                        replica_instance = replica_response["DBInstances"][0]
                        replica_name = replica_instance["DBInstanceIdentifier"]
                        if replica_name.endswith("-read-replica"):
                            result["replica"] = {
                                "endpoint": replica_instance["Endpoint"]["Address"],
                                "instance_name": replica_name,
                            }
                        elif replica_name.endswith("-data-replica"):
                            result["datareplica"] = {
                                "endpoint": replica_instance["Endpoint"]["Address"],
                                "instance_name": replica_name,
                            }

                return result
            else:
                print(f"No RDS instance found with name: {instance_name}")
                return None
        except ClientError as e:
            print(f"Error retrieving RDS instance: {e}")
            return None
