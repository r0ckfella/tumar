# tumar-backend

A RESTful Django backend system for monitoring multiple GPS trackers.. Check out the project's [swagger (interactive API on a web page)](http://tumarb.winext.kz/swagger/).

<br>

## Local Development Setup

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (not anaconda) for Python 3.7+ (to check whether the conda is installed run ```conda info```)

    > :information_source: You don't need to install Python 3.6 externally for this project. Miniconda environment installs the correct Python version in the third step. 

    Then run the following commands:

    ```shell
    conda config --add channels conda-forge
    conda config --set channel_priority strict
    ```    

<br>

2. Open the file named ```environment.yml``` in the project's root directory (where ```manage.py``` file exists). 

    Then change the *prefix* line which is shown below:
    
    - *USER* is the system user you use
    - *MINICONDA_DIRECTORY* is the folder name where you installed miniconda

    ```
    prefix: /home/{USER}/{MINICONDA_DIRECTORY}/envs/tumar_dev
    ```

    <br>

3. Create an environment. The below command uses the ```environment.yml``` file:

    ```shell
    conda env create
    ```

    <br>

4. Set up the database using postgres cli (command line interface) which was installed in the environment from the previous step:

    ```shell
    initdb -D base_db # create a base database locally

    pg_ctl -D base_db -l logfile start # start the PostgreSQL server
    ```

    <br>

    Now create a user and create the *tumar* database setting the user as the owner:

    ```shell
    createuser --encrypted --pwprompt tumar_user # tumar_user can be changed
    
    createdb --owner=tumar_user tumar_db # tumar_db can be changed
    ```

    > :information_source: After computer turns off and turns on, postgres database needs to be started, you can use predefined Make command ```make start-db``` (you should start it only once when you turn on your computer)

    <br>

    Enter the PostgreSQL shell as superuser which is the current user you are logged in as.

    ```shell
    psql -h localhost -d tumar_db
    ```

    In the shell add the PostGIS extension to the *tumar* database. This adds support for geographical data.

    ```
    tumar_db=# CREATE EXTENSION postgis;
    ```

    <br>

5. Create ```.env``` file in the project's root directory and populate it with sensitive data (you can ask the admin):


    > :information_source: This version of ```.env``` file is only for local development. In production environment it has additional key value pairs!

    <br>

    > :warning: Remove the comments otherwise Django wouldn't read ```.env`` file correctly!

    ```
    DJANGO_SECRET_KEY="" # this is a string that you can generate (google "generate Django secret key")
    DJANGO_CONFIGURATION="Local"
    DJANGO_SETTINGS_MODULE="tumar.config"
    TUMAR_DB="postgis://tumar_user:test_password@localhost:5432/tumar_db" # insert your own user and password
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

<br>

6. Configure Django. The first command creates tables in *tumar_db*. The second command creates a superuser or an admin:

    ```shell
    python manage.py migrate
    python manage.py createsuperuser
    ```

<br>

## Every time start the development server using predefined Makefile commands:

```shell
make start-db # You should start tumar_db only once when you start your PC
make start-dev # migrates, and runs dev server
```

> :information_source: You can inspect ```Makefile``` file in the project's root directory to understand which commands are invoked! I decided to use Makefile since it is the oldest standard and it is technology-agnostic.

> :information_source: To stop the database instance, firstly, check whether it is running by executing ```ps aux | grep postgres``` (Ignore the line that ends with ```grep --color=auto postgres```). The database instance corresponds to the line ending with 'postgres -D /path/to/tumar_db'. The second column of this line is the process ID that we need. Finally, run ```kill <process id>``` .

<br>

## Deploy process

1. Add remote server's sensitive SSH data (ask the admin for the data) to local ```.env``` file:
    

    
    ```
    DEPLOY_SSH_USER="test_user"
    DEPLOY_SSH_IP="192.168.0.1"
    DEPLOY_SSH_PORT="8080" # port is optional
    ```

2. After adding code and commiting it to GitHub. Start the automatic deployment shell script from the project's root directory. This script prompts server's SSH password to continue the deployment process:


    ```shell
    ./deploy/initiate.sh 
    ```

> :information_source: The remote server already contains ```.env``` file in the project's root directory.

<br>

## Useful Commands

#### PostgreSQL commands
    

- Connect to psql terminal as user:


    ```shell
    psql -U tumar_user -h localhost -d tumar_db
    ```

- Back up a database into a ```.bak``` file:


    ```shell
    pg_dump -U <database_user> -h <ip_address> -p <port> -Fc <database_name> > <file_name>.bak
    ```

- Restore a database from a ```.bak``` file:


    ```shell
    pg_restore -C -U <database_user> -h <ip_address> -p <port> -d <database_name> < <file_name>.bak
    ```

**Commands below are executed inside psql terminal.**

- List all databases:


    ```sql
    \l
    ```

- Connect to a database:


    ```sql
    \c <database_name>
    ```

- List all tables in the current database:


    ```sql
    \dt
    ```

- Delete a database:


    ```sql
    DROP DATABASE <database_name>
    ```

- List all users:


    ```sql
    \du
    ```

- Delete a user:


    ```sql
    DROP USER <username>
    ```

#### Conda Environment Commands

- Activate conda environment in the current terminal:


    ```shell
    conda activate ENVNAME
    ```

- Deactivate conda environment in the current terminal:


    ```shell
    conda deactivate
    ```

- List all packages and versions in the active environment:


    ```shell
    conda list
    ```

- Delete an environment:


    ```shell
    conda remove --name ENVNAME --all
    ```

- Export an environment to a YAML (```environment.yml```) file:


    ```shell
    conda env export --no-builds --name ENVNAME > environment.yml
    ```

- Detailed information about package versions:


    ```shell
    conda search PKGNAME --info
    ```

- Install package from a specific channel:


    ```shell
    conda install conda-forge::PKGNAME
    ```

- Install a package by exact version number (3.1.4):


    ```shell
    conda install PKGNAME==3.1.4
    ```

- Remove unused cached files including unused packages:


    ```shell
    conda clean --all
    ```

- Remove a package from an environment:


    ```shell
    conda uninstall PKGNAME --name ENVNAME
    ```

#### Git Commands

- Отменить последний коммит не удаляя написанный код:


    ```shell
    git reset HEAD~
    ```