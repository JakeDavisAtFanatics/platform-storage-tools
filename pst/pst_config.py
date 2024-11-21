import os
import yaml  # type: ignore
import argparse
from typing import Dict, List
from pst.aws_sso import AwsSsoService
from pst.aws_rds import AwsRdsService
from pst.aws_ssm import AwsSsmService


def load_yaml_config(file_path: str) -> Dict:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def save_yaml_config(file_path: str, data: Dict):
    with open(file_path, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


def get_available_environments() -> List[str]:
    config_dir = os.path.expanduser("~/.pst/config")
    return [f.split(".")[0] for f in os.listdir(config_dir) if f.endswith(".env.yaml")]


def pst_config(environment: str = None):
    environments = get_available_environments()
    environments.append("all")

    if not environment:
        print("Available environments:")
        for i, env in enumerate(environments, 1):
            print(f"{i}. {env}")

        choice = int(input("Select an environment (enter the number): ")) - 1
        environment = environments[choice]

    config_dir = os.path.expanduser("~/.pst/config")
    if environment == "all":
        env_files = [f for f in os.listdir(config_dir) if f.endswith(".env.yaml")]
    else:
        env_files = [f"{environment}.env.yaml"]

    aws_sso = AwsSsoService()

    for env_file in env_files:
        config_path = os.path.join(config_dir, env_file)
        config = load_yaml_config(config_path)

        if environment == "local":
            # For local environment, only update pgpass without modifying the config file
            for cluster_name, cluster_config in config["clusters"].items():
                for role, role_info in cluster_config["roles"].items():
                    hostname = role_info["endpoint"]
                    port = role_info["port"]
                    database = "*"
                    username = "postgres"
                    password = "password"
                    update_pgpass(hostname, port, database, username, password)
                    print(f'  Updated pgpass for role: "{role}" in cluster: "{cluster_name}"')
            print(f"Processed local environment without modifying {env_file}")
        else:
            for cluster_name, cluster_config in config["clusters"].items():
                aws_account_name = cluster_config["aws_account_name"]
                aws_region = cluster_config["aws_region"]
                environment_name = cluster_config["environment_name"]
                profile_name = f"{aws_account_name}.AdministratorAccess"

                try:
                    aws_sso.authenticate(profile_name)
                    session = aws_sso.get_session()

                    aws_rds = AwsRdsService(session)
                    rds_info = aws_rds.get_rds_instance(environment_name, aws_region)

                    if rds_info:
                        cluster_config["roles"] = rds_info
                        print(f'Processing cluster: "{environment_name}-postgresql"')

                        # Update pgpass file for each role
                        aws_ssm = AwsSsmService(session, aws_region)
                        for role, role_info in rds_info.items():
                            hostname = role_info["endpoint"]
                            port = "5432"  # Assuming default PostgreSQL port
                            database = "postgres"  # Assuming default database name
                            username = aws_ssm.get_parameter(
                                f"/{environment_name}/database/master-user"
                            )
                            password = aws_ssm.get_parameter(
                                f"/{environment_name}/database/master-pass"
                            )

                            if username and password:
                                update_pgpass(hostname, port, database, username, password)
                                print(f'  Updated pgpass for role: "{role}"')
                            else:
                                print(
                                    f'  Failed to retrieve credentials for role: "{role}"'
                                )

                except Exception as e:
                    print(f"Error processing cluster {cluster_name}: {e}")
                    print("Skipping this cluster and continuing with the next one.")
                finally:
                    print("---")  # Add a separator between clusters for better readability

            save_yaml_config(config_path, config)
            print(f"Updated configuration for {env_file}")


def update_pgpass(
    hostname: str, port: str, database: str, username: str, password: str
):
    pgpass_path = os.path.expanduser("~/.pgpass")
    entry = f"{hostname}:{port}:{database}:{username}:{password}\n"

    # Create the file if it doesn't exist
    if not os.path.exists(pgpass_path):
        with open(pgpass_path, "w"):
            pass
        os.chmod(pgpass_path, 0o600)  # Set permissions to read/write for the owner only

    # Check if the entry already exists
    with open(pgpass_path, "r") as f:
        if entry in f.read():
            return  # Entry already exists, no need to add it again

    # Append the new entry
    with open(pgpass_path, "a") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(description="PST Config Tool")
    parser.add_argument("environment", nargs="?", help="Environment to configure")
    args = parser.parse_args()

    pst_config(args.environment)


if __name__ == "__main__":
    main()
