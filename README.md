# Observer

![Build Status](https://github.com/tamizhgeek/observer/workflows/Test%20and%20Build/badge.svg)

Observer is a tool to monitor websites. You can configure uptime, status and regex based checks for websites and store the check results into a PostgreSQL database via Kafka.


### Requirements

- Python 3.7+
- PostgreSQL 11 (It probably works with < 11 versions as well, but wasn't tested)
- Kafka 2.4

### Setup

#### Build and Install

The project follows the standard setup.py based installation.

```bash
cd observer
python -m pip install --upgrade pip
pip install setuptools wheel pipenv
python setup.py install
```

or in a single step:

```bash
./install.sh
```

This will install three executables into your `$PATH`

1. `observer_source`
2. `observer_sink`
3. `observer_fixtures`

More details on how to use those in the section below.

## Usage

Observer has two components:

1. Source, and 
2. Sink


### Source

Source is a tool to monitor websites and publish the monitoring results into a Kafka topic.
The website checks have the following config:

```yaml
- url: https://google.com
  frequency: 3
  regex:
    - name: check_google_exists
      pattern: .*google.*
```

`url`: The url to monitor

`frequency`: How often to monitor the above url (The value should be in seconds. Only whole numbers are allowed)

`regex`: There can be multiple regex checks. Each regex check should have a unique name and a pattern which will be used to check
the content of the webpage returned in the above url. The monitoring result will contain True/False for each regex check
to denote if the pattern is found on the page or not.  

There is a sample `checks.yml` file inside the config directory. 

The source also needs access to a PostgreSQL database. The config for the same is provided as an example in the `config.ini` file inside the `config` directory.

To run the source, we need to specify a directory from which our tool can read configuration from. 
This can be provided using a ENV variable `OBSERVER_CONFIG_DIR`. By default, the configs are read from the config
directory, but this needs to be overridden with actual values before running. So do the following steps:

1. Create a directory to store configuration
2. Create a `checks.yml` file and add the required checks to monitor.
3. Create a `config.ini` file and fill the parameters for connecting to Kafka and PostgreSQL.

```bash
EXPORT OBSERVER_CONFIG_DIR=<config_dir_you_created_above>
observer_source
```

This will start the source tool and it will start monitoring the websites you configured. The logs are always sent to the stderr. 
It is recommended to run this tool and the sink tool using a processor manager such as supervisor.

### Sink

Sink is a tool to complement the Source. It will read the monitoring
results from Kafka and store them into a PostgreSQL database. To run the Sink, you need
to follow the almost same procedure as mentioned above. You don't need to create the checks.yml while configuring Sink.
If both Source and Sink are running on the same node, they can share the `config.ini` configuration. There is an option to
supply the DB password via a ENV var (`OBSERVER_DB_PASSWORD`) if required.

Before starting Sink, you need to initialize the database.  

#### Fixtures

To make the DB initialization easier, we also provide another tool. 

*_WARNING_*: Run this only once before you setup Sink. 

```bash
EXPORT OBSERVER_CONFIG_DIR=<config_dir_you_created_above>
# the below will do a dry-run
observer_fixtures
# To run the actual initialization
observer_fixtures --live
``` 

Once the database is ready, the sink can be started as:

```bash
EXPORT OBSERVER_CONFIG_DIR=<config_dir_you_created_above>
observer_sink
```


### Development Setup

This project uses Pipenv for development

checkout the project and cd into the project dir.
```$bash
pipenv install --dev
```

#### Tests

To run the unit tests:

```bash
pipenv run pytest
```

Running unitests still needs internet access to access websites mentioned in the check configs
and a PostgreSQL database. The configuration for the same is provided via the
[config.TEST.ini](config/config.TEST.ini). The configurations are pretty self explanatory. 

There is an end to end integration test in [test_source_and_sink_integration.py](tests/integration/test_source_and_sink_integration.py) which is skipped by default,
since it requires SSL configuration to talk to Kafka cluster. To run it, you need to supply the
CA certificate and Access key and certificate and configure the filenames in the 
config file. Again, the `config.TEST.ini` has good reference values.

## Releasing

The project has no published binaries yet. But platform specific wheels can be built using the setuptools in the future.