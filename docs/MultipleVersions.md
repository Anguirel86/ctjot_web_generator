# Running Additional Web Generators

These are the instructions for setting up additional containers running the web generator.
This can be useful for setting up a beta site or any other custom version of the web 
generator without modifying the base deployment files.

These instructions are based off of some notes I took while experimenting.  There may be 
a better way to do this.  The instructions will assume we're setting up a beta server and 
that **a staging or production copy of the release site is already running**.


## Setting up a working area

Create a fresh working area for the beta site and clone the web generator:
  1. `mkdir beta_generator`
  2. `cd beta_generator`
  3. `git clone https://github.com/Anguirel86/ctjot_web_generator.git`
  4. Copy a vanilla, unheadered Chrono Trigger ROM to the repo base directory as ct.sfc

Check out the beta branch and initialize the randomizer submodule
  4. `git checkout beta_integration`
  5. `git submodule init`
  6. `git submodule update`

## Setting up the container

We'll need to create a new docker-compose file and set up the environment so that it 
plays nicely with the existing containers.

  1. `cd deploy`
  2. `cp docker-compose.prod.yml docker-compose.beta.yml`
  3. Open the new docker-compose file
  4. Remove all services except the web-generator
  5. Remove all named volumes (Except for static_volume)
  6. Rename the web-generator service to beta-web-generator
  7. Remove the db dependency

Set up the environment files.

Update .env.prod
  1. Set the new hostname for this generator in the following variables:
     1. DJANGO_ALLOWED_HOSTS, 
     2. VIRTUAL_HOST, 
     3. LETSENCRYPT_HOST
  2. Set up a DJANGO_SECRET_KEY
     1. `python3 -c "import secrets; print(secrets.token_urlsafe())`
     2. Copy the output from that to the SECRET_KEY variable

Update .env.prod.db
  1. Set the POSTGRES_PASSWORD variable to the value of the running release web generator
  2. Change the POSTGRES_DB name to `ctjot_beta`

Update .env.prod.letsencrypt
  1. Set an email address to be used for certificates

Update the webapp settings to serve static files from a beta directory:
  1. Change static files variables in ctjot/settings.py
     1. Change STATIC_URL to 'static/beta'
     2. change STATIC_ROOT to BASE_DIR / "staticfiles/beta"

## Updating the database

The new beta database will have to be added to the database server manually.

  1. `docker exec -ti deploy_db_1 /bin/bash`
  2. `su postgres`
  3. `createdb -U ctjot -W ctjot_beta`
  4. enter the database password when prompted

## Build the container

Now that the docker-compose and environment files are all set up, it's time to build the container.

From the repository root directory:
`docker-compose -f deploy/docker-compose.beta.yml build`

## Run the container

Running the container will start the beta web generator.  The nginx reverse proxy running in the
release setup will notice the new container and dynamically reconfigure itself based on the
settings in the .env.prod and .env.prod.letsencrypt files.

`docker-compose -f deploy/docker-compose.beta.yml up -d`

This will run the container in detached mode (in the background).

If you accidentally forget the -d flag,
```
ctrl + z
bg
```
to move the process to the background.

## Applying future updates

The beta site will change over time as more work is done and new features are introduced.
To apply those changes:

```shell
# Bring the beta container down
docker-compose -f deploy/docker-compose.beta.yml rm -s -v beta-web-generator

# Update the repo and randomizer submodule
git pull
git submodule update

# Rebuild and restart the container
docker-compose -f deploy/docker-compose.beta.yml up --build -d
```
