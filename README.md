# tumar-backend

A RESTful Django backend system for monitoring multiple GPS trackers.. Check out the project's [swagger (interactive API on a web page)](http://tumarb.winext.kz/swagger/).

<br>

## Local Development Setup

1. Install [Conda](https://docs.conda.io/en/latest/miniconda.html) (not anaconda) for Python 3.7+ (to check whether the conda is installed run ```conda info```)

<br>

2. Create an environment from the file named ```environment.yml``` in the project's root directory (where ```manage.py``` file exists):
    
    <br>

    ```shell
    conda env create
    ```

3. Create database using postgres cli (command line interface) which was installed in the environment from the previous step:
    
    <br>
    
    ```shell
    export PGDATA=./pgdata
    mkdir $PGDATA # creates a directory with the name "pgdata" in the current directory
    pg_ctl initdb 
    pg_ctl start
    psql -c "create database tumar;" postgres # creates a database with the name "tumar"
    ```

    When you are connected to the **psql** terminal, create user and give him permissions for the *tumar* database (do not forget ; symbol at the end of a line):
    
    <br>

    ```sql
    CREATE USER tester WITH PASSWORD 'test_password'; # come up with your own user and password
    GRANT ALL PRIVILEGES ON DATABASE 'tumar' to tester;
    ```

    > :information_source: After computer turns off and turns on, postgres database needs to be started, you can use predefined Make command ```make start-db``` (you should start it only once when you turn on your computer)

    <br>

4. Create ```.env``` file in the project's root directory and populate it with sensitive data (you can ask the admin):

    <br>

    > :information_source: This version of ```.env``` file is only for local development. In production environment it has additional key value pairs!

    ```
    DJANGO_SECRET_KEY="" # this is a string that you can generate (google "generate Django secret key")
    DJANGO_CONFIGURATION="Local"
    DJANGO_SETTINGS_MODULE="tumar.config"
    TUMAR_DB="postgis://tester:test_password@localhost:5432/tumar" # insert your own user and password
    DOWNLOAD_GEOLOCATIONS_URL="" # ask the rest of the data from the admin
    GET_BATTERY_CHARGE_URL=""
    CHINESE_LOGIN_URL=""
    STANDARD_LOGIN_PASSWORD=""
    TELEGRAM_BOT_TOKEN=""
    TELEGRAM_CHAT_ID=""
    MEMCACHED_ADDRESS="127.0.0.1:11211"
    EGISTIC_CADASTRE_QUERY_URL=""
    EGISTIC_LOGIN_URL=""
    EGISTIC_USERNAME=""
    EGISTIC_PASSWORD=""
    ```

---
> :information_source: If you want to use caching when developing, you can start memcached service in another terminal: ```memcached -m 1024 -l 127.0.0.1 -p 11211```
---

5. Start development server using predefined Makefile commands:
    
    <br>

    > :information_source: You can inspect ```Makefile``` file in the project's root directory to understand which commands are invoked! I decided to use Makefile since it is the oldest standard and it is technology-agnostic.

    ```shell
    make start-db # start postgres database only once when you start your PC
    make start-dev # migrates, and runs dev server
    ```

<br>

## Deploy process

1. Add remote server's sensitive SSH data (ask the admin for the data) to local ```.env``` file:
    
    <br>
    
    ```
    DEPLOY_SSH_USER="test_user"
    DEPLOY_SSH_IP="192.168.0.1"
    DEPLOY_SSH_PORT="8080" # port is optional
    ```

2. After adding code and commiting it to GitHub. Start the automatic deployment shell script from the project's root directory. This script prompts server's SSH password to continue the deployment process:

    <br>

    ```shell
    ./deploy/initiate.sh 
    ```

> :information_source: The remote server already contains ```.env``` file in the project's root directory.

<br>

## Useful Commands

#### PostgreSQL commands
    

- Connect to psql terminal using root user if you forgot user and password:

    <br>

    ```shell
    sudo -u postgres psql
    ```

- Back up a database into a ```.bak``` file:

    <br>

    ```shell
    pg_dump -U <database_user> -h <ip_address> -p <port> -Fc <database_name> > <file_name>.bak
    ```

- Restore a database from a ```.bak``` file:

    <br>

    ```shell
    pg_restore -C -U <database_user> -h <ip_address> -p <port> -d <database_name> < <file_name>.bak
    ```

**Commands below are executed inside psql terminal.**

- List all databases:

    <br>

    ```sql
    \l
    ```

- Connect to a database:

    <br>

    ```sql
    \c <database_name>
    ```

- List all tables in the current database:

    <br>

    ```sql
    \dt
    ```

- Delete a database:

    <br>

    ```sql
    DROP DATABASE <database_name>
    ```

- List all users:

    <br>

    ```sql
    \du
    ```

- Delete a user:

    <br>

    ```sql
    DROP USER <username>
    ```

#### Conda Environment Commands

- Activate conda environment in the current terminal:

    <br>

    ```shell
    conda activate ENVNAME
    ```

- Deactivate conda environment in the current terminal:

    <br>

    ```shell
    conda deactivate
    ```

- List all packages and versions in the active environment:

    <br>

    ```shell
    conda list
    ```

- Delete an environment:

    <br>

    ```shell
    conda remove --name ENVNAME --all
    ```

- Export an environment to a YAML (```environment.yml```) file:

    <br>

    ```shell
    conda env export --name ENVNAME > environment.yml
    ```

- Create an environment from the file named ```environment.yml``` in the current directory file:

    <br>

    ```shell
    conda env create
    ```

- Detailed information about package versions:

    <br>

    ```shell
    conda search PKGNAME --info
    ```

- Search for a package in currently configured channels with version range >=3.1.0, <3.2:

    <br>

    ```shell
    conda search PKGNAME=3.1 "PKGNAME [version='>=3.1.0,<3.2']"
    ```

- Install package from a specific channel:

    <br>

    ```shell
    conda install conda-forge::PKGNAME
    ```

- Install a package by exact version number (3.1.4):

    <br>

    ```shell
    conda install PKGNAME==3.1.4
    ```

- Install following several constraints (AND):

    <br>

    ```shell
    conda install "PKGNAME>2.5,<3.2"
    ```

- Add a channel to your Conda configuration:

    <br>

    ```shell
    conda config --add channels CHANNELNAME
    ```

- Remove unused cached files including unused packages:

    <br>

    ```shell
    conda clean --all
    ```

- Remove a package from an environment:

    <br>

    ```shell
    conda uninstall PKGNAME --name ENVNAME
    ```

- Remove a package from an environment:

    <br>

    ```shell
    conda uninstall PKGNAME --name ENVNAME
    ```

- Run most commands without requiring a user prompt (useful for scripts):

    <br>

    ```shell
    conda install --yes PKG1 PKG2
    ```

- Examine Conda configuration and configuration services:

    <br>

    ```shell
    conda config --show
    conda config --show-sources
    ```

#### Git Commands

- Отменить последний коммит не удаляя написанный код:

    <br>

    ```shell
    git reset HEAD~
    ```