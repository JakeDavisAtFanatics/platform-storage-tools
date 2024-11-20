import os
import yaml  # type: ignore
import argparse
import subprocess
from typing import Dict, List


def load_yaml_config(file_path: str) -> Dict:
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_available_environments() -> List[str]:
    config_dir = os.path.expanduser("~/.pst/config")
    return [f.split(".")[0] for f in os.listdir(config_dir) if f.endswith(".env.yaml")]


def print_options(options: List[str], title: str):
    print(f"\n{title}:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")


def get_selection(options: List[str], prompt: str) -> str:
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def process_config(env: str, cluster: str = None, role: str = None):
    config_dir = os.path.expanduser("~/.pst/config")
    config_path = os.path.join(config_dir, f"{env}.env.yaml")
    config = load_yaml_config(config_path)
    print_command_for_next_time = cluster is None or role is None

    if not cluster:
        clusters = list(config["clusters"].keys())
        print_options(clusters, "Available clusters")
        cluster = get_selection(clusters, "Select a cluster (enter the number): ")

    if not role:
        roles = list(config["clusters"][cluster]["roles"].keys())
        print_options(roles, "Available roles")
        role = get_selection(roles, "Select a role (enter the number): ")

    role_info = config["clusters"][cluster]["roles"][role]
    endpoint = role_info["endpoint"]
    instance_name = role_info["instance_name"]

    # Construct psql command
    custom_prompt = f"{instance_name} %/=> "
    psql_command = f"psql -h {endpoint} -d postgres -p 5432 -U postgres -v PROMPT1='{custom_prompt}'"

    # Execute psql command
    try:
        env_vars = os.environ.copy()
        env_vars["PGPASSFILE"] = os.path.expanduser("~/.pgpass")
        if print_command_for_next_time:
            print(f"\nCommand for next time: pg {env} {cluster} {role}\n")
        subprocess.run(psql_command, shell=True, check=True, env=env_vars)
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to the database: {e}")


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL Interactive Tool")
    parser.add_argument("environment", nargs="?", help="Environment name")
    parser.add_argument("cluster", nargs="?", help="Cluster name")
    parser.add_argument("role", nargs="?", help="Role name")
    args = parser.parse_args()

    if not args.environment:
        environments = get_available_environments()
        print_options(environments, "Available environments")
        args.environment = get_selection(
            environments, "Select an environment (enter the number): "
        )

    process_config(args.environment, args.cluster, args.role)


if __name__ == "__main__":
    main()
