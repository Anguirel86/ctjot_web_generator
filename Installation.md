# Installation and Running Instructions
These are the instructions for setting up the web generator.

## Getting started
This section details how to download and set up the ctjot web generator. 
There are two options: running locally or running in Docker.

### Clone the repo
Browse to your working area and:
`git clone https://github.com/Anguirel86/ctjot_web_generator.git`

The Jets Of Time randomizer is included in this repo as a submodule.  It will need to be initialized.
If running with the deploy.sh script then this will be handled automatically.  If not, then run:
 1. `git submodule init`
 2. `git submodule update`

### Vanilla ROM
 1. Copy an unheadered Chrono Trigger ROM to the repo base directory and name it ct.sfc

### Running Locally
The web generator can be run using the built-in Django test server and sqlite database.  By default,
this server will only be accessible on localhost.

#### Set up a Python virtual environment

 1. Create a virtual environment named venv:
    1. `python3 -m venv venv`
 2. Enter the virtual environment:
    1. `source venv/bin/activate` (Linux)
    2. `source venv/Scripts/activate` (Windows)
 3. Install dependencies:
    1. `pip install -r requirements.txt`

#### Run the server

 1. Set a SECRET_KEY.  Either:
    1. Set the SECRET_KEY environment variable, or
    2. Modify the SECRET_KEY line in the ctjot/settings.py file
 2. Set the app to DEBUG mode.  Either:
    1. Set the DEBUG environment variable to '1' or
    2. Modify the DEBUG line in the ctjot/settings.py file
    3. This will allow the test server to see static files and allow tracebacks on errors
 3. Copy or link the following files into the web app's base directory:
    1. jetsoftime/sourcefiles/names.txt
    2. jetsoftime/sourcefiles/patch.ips
    3. jetsoftime/sourcefiles/flux/
    4. jetsoftime/sourcefiles/patches/
    5. jetsoftime/sourcefiles/pickles/
 4. Enter the virtual environment (if not already done):
    1. `source venv/bin/activate` (Linux)
    2. `source venv/Scripts/activate` (Windows)
 5. Apply database migrations:
    1. `python manage.py migrate`
 6. Run the test server:
    2. `python manage.py runserver`

### Running the web generator with Docker and the deploy.sh script
The repo contains a deploy.sh script that will verify the environment and build/launch the containers.

There are three supported deployment types:
 1. Development
    1. Only the web app and database containers, runs with the built-in Django test server
 2. Staging
    1. Runs all containers using the letsencrypt staging API and fewer environment checks
 3. Production
    1. Runs the full production setup with the live letsencrypt API and full environment checks

#### Development
This is a configuration is meant for local testing of the web generator.  It launches a minimal subset
of containers needed for testing, and is not suited for use in a production environment. 

Run the deployment script from the repo root directory.
 1. `./deploy/deploy.sh -d`
 2. Open a web browser and point it to the webapp on port 8000:
    1. ie: http://localhost:8000
 
#### Staging
This configuration runs the web generator in a near production environment with all containers.
It uses the letsencrypt staging API due to the higher rate limit.  This results in self-sighed
certificates, so browsers will give security warnings.
 1. Set an email address in deploy/.env.staging.letsencrypt
    1. This is the email address used to register the certificates
 2. (Optional) Update the hostnames in the following environment files if not using test.ctjot.com
    1. deploy/.env.staging
       1. Update DJANGO_ALLOWED_HOSTS, VIRTUAL_HOST, and LETSENCRYPT_HOST with the new hostname
    2. deploy/.env.staging.wiki
       1. Update VIRTUAL_HOST and LETSENCRYPT_HOST with the new hostname
 3. `./deploy/deploy.sh -s`
 4. Open a web browser and point it to the webapp
    1. ie: https://test.ctjot.com
    2. NOTE: You will need to add a security exception due to the self-signed certificate

#### Production
This configuration deploys a full production version of the web generator.
1. Set an email address in deploy/.env.prod.letsencrypt
    1. This is the email address used to register the certificates
2. Set a password for the database in deploy/.env.prod.db
3. (Optional) Update the hostnames in the following environment files if not using ctjot.com
   1. deploy/.env.prod
      1. Update DJANGO_ALLOWED_HOSTS, VIRTUAL_HOST, and LETSENCRYPT_HOST with the new hostname
   2. deploy/.env.prod.wiki
      1. Update VIRTUAL_HOST and LETSENCRYPT_HOST with the new hostname
4. `./deploy/deploy.sh -p`
5. Open a web browser and point it to the webapp
   1. ie: https://ctjot.com

#### Shutdown and Restart the containers
The deploy.sh script has options to stop and restart the last run configuration.

1. `./deploy/deploy.sh -k` will shut down the web generator.
2. `./deploy/deploy.sh -r` will rerun the last run configuration

The docker-compose yaml file used for the last run configuration is linked in deploy/docker-compose.yml.
This can be used for any manual docker-compose commands.

#### Wiki data migration
This is an optional step that can be run to migrate existing (non containerized) DokuWiki data 
into the DokuWiki container volume.  This will copy page data, user settings, plugins, etc.

1. Tar up the entire dokuwiki directory on the live server.
   1. `tar -czvf wiki_data.tar /path/to/wiki`
2. Copy wiki_data.tar to the new host and untar it in a temp location
   1. `tar -xvf wiki_data.tar`
3. Run either a staging or production deployment at least once to initialize the wiki volume
4. Bring the webapp down
   1. `./deploy/deploy.sh -k`
5. Run the wiki migration
   1. NOTE: This will require root since some wiki conf data is owned by root in the container
   2. `./deploy/deploy.sh -w /path/to/wiki/backup`
   3. Enter your password when prompted
6. Rerun the webapp
   1. `./deploy/deploy.sh -r`
7. Browse to the wiki and verify the data migrated successfully
   1. ie: https://wiki.test.ctjot.com for the default staging address
   

