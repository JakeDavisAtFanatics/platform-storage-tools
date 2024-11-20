# PST (Platform Storage Tools)

PST is a collection of tools for PostgreSQL database management and environment configuration.

## Installation

Create and activate a virtual environment:

```bash
# This path is required.
python3 -m venv ~/.pst
source ~/.pst/bin/activate
```

Install PST:

```bash
pip install .
```

Copy configs:

```bash
# This path is required
cp -R config ~/.pst
```

## Usage

To use PST, you must first always activate the virtual environment:

```bash
source ~/.pst/bin/activate
```

### pst-config

This tool will initialize PST config files:
- Find RDS instances and replicas and add them to `config/*.env.yaml`
- Configure each RDS instance in `~/.pgpass` 

```bash
pst-config [-h] [environment]

# List all available environments
pst-config

# Initialize dev
pst-config dev
```

### pg

This tool can be used interactively to find and connect to RDS instances. Or connect to RDS quickly with a full command.

```bash
pg [-h] [environment] [cluster] [role]

# List all available environments
pg

# List all available clusters in dev
pg dev

# List all available roles in dev parent
pg dev parent

# Connect to the data replica in dev parent
mm dev parent datareplica
```

## Configuration

Environment configurations are stored in YAML files in the `config/` directory. Each file should follow the format `<environment>.env.yaml`.

This is an example to add a Hawaii cluster to dev. Add the minimum required cluster details to the yaml:

```yaml
clusters:
  ha:
    aws_account_name: sportsbook-hi-1-dev
    aws_region: us-east-2
    environment_name: fbg-dev-1hi
```

Then initialize dev:

```bash
pst-config dev
```

