# PST (Platform Storage Tools)

PST is a collection of tools for PostgreSQL database management and environment configuration.

## Installation

Create and activate a virtual environment:
- This path is required `~/.pst`

```bash
python3 -m venv ~/.pst && source ~/.pst/bin/activate
```

Install PST:

```bash
pip install .
```

Copy base configs:

```bash
cp -R config ~/.pst
```

## Usage

To use PST, you must first always activate the virtual environment:

```bash
source ~/.pst/bin/activate
```

### pst-config

This tool will initialize PST config files:
- Find RDS instances and replicas and add them to `~/.pst/config/*.env.yaml`
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
pg dev parent datareplica
```

### pg_repack

Build the `pg_repack` Docker containers:

```bash
# Build pg_repack for Postgres 13
docker build docker/pg_repack_1.4.6_for_pg_13 -t pst/pg-repack-1.4.6

# Build pg_repack for Postgres 16
docker build docker/pg_repack_1.5.0_for_pg_16 -t pst/pg-repack-1.5.0

# Build pg_repack for Postgres 17
docker build docker/pg_repack_1.5.1_for_pg_17 -t pst/pg-repack-1.5.1
```

Create aliases to wrap the Docker command:
- These mount your local pgpass to the container to handle authentication

```bash
alias pg_repack@13="docker run -v ~/.pgpass:/root/.pgpass:ro -it --rm --network host pst/pg-repack-1.4.6 pg_repack"
alias pg_repack@16="docker run -v ~/.pgpass:/root/.pgpass:ro -it --rm --network host pst/pg-repack-1.5.0 pg_repack"
alias pg_repack@17="docker run -v ~/.pgpass:/root/.pgpass:ro -it --rm --network host pst/pg-repack-1.5.1 pg_repack"
```

Use the aliases as you would the `pg_repack` tool normally:

```bash
$ pg_repack@17 --version
pg_repack 1.5.1

$ pg_repack@17 -h 127.0.0.1 -p 7432 -U postgres --dbname=ats_fanatics --table=jobs.batch_step_execution --dry-run
INFO: Dry run enabled, not executing repack
INFO: repacking table "jobs.batch_step_execution"
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

