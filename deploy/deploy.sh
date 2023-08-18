#!/usr/bin/env bash

#
# This script performs setup and deployment of the web generator in Docker containers.
# It allows for either a production, staging, or development deployment.
#

check_and_set_env_vars() {
  set +e

  if ! builtin command -v "docker" >/dev/null; then
    echo "You must install docker to use this script."
    exit 1
  fi

  # determine docker-compose command, preferring "docker compose"
  dcver="$(docker compose version)"
  ret=$?

  set -e

  if (( ret == 0 )); then
    echo "Using docker compose (version: $dcver)"
    DCCMD="docker compose"
  else
    # check that $DCCMD is available
    if ! builtin command -v "docker-compose" >/dev/null; then
      echo "You must update docker to a version with compose or install docker-compose to use this script."
      exit 1
    fi
    dcver="$(docker-compose version)"
    echo "Using docker-compose (version: $dcver)"
    DCCMD="docker-compose"
  fi
  export DCCMD

  COMPOSE_FILE="${COMPOSE_FILE:-$PWD/deploy/docker-compose.yml}"
  export COMPOSE_FILE

  set +e
}

#
# Copy the ctjot wiki data into the DokuWiki container's config area. This is used
# for the initial migration from the standalone setup to the containerized setup.
# Moving forward we can just backup the whole config directory rather than doing
# this in a piecemeal fashion.
#
# Arguments:
#     $1 - Path to a backup of the wiki
#
# Prerequisite: 
#     This function should not be run until the wiki container has run at least once
#     and set up the config area.  We will be replacing the wiki contents in that
#     folder with our own wiki data.
#
migrate_dokuwiki_data() {

  # Make sure the target config directory exists.  If not then the wiki container
  # hasn't been run yet and we can't migrate our data to it.
  if [[ ! -d "deploy/wiki_config/dokuwiki" ]]; then
    echo "DokuWiki config data doesn't exist.  Run the DokuWiki container before migrating data."
    exit 1
  fi

  WIKIDATA="$1"

  if [[ ! -d $WIKIDATA ]]; then
    echo "Missing wiki backup folder argument"
    exit 1
  fi

  # Array of data directories we need to copy our wiki data into
  # Some of these directories need root access to copy
  declare -a dokudirs=("pages" "attic" "meta" "media" "media_attic" "media_meta")

  echo "Copying wiki data..."
  echo "This requires root permission"
  # Copy over the data folders
  for dir in "${dokudirs[@]}"; do
    if [[ ! -d ${WIKIDATA}/data/${dir} ]]; then
      echo "Can't find ${WIKIDATA}/${dir}"
      exit 1
    fi

    echo "Copying ${WIKIDATA}/data/${dir}..."
    sudo cp -r "${WIKIDATA}/data/${dir}/"* "deploy/wiki_config/dokuwiki/data/${dir}/"
  done

  # Files will be owned by a mix of root and the docker container user.
  # Chown the copied files to the container user to avoid permissions issues.
  sudo chown 1000:911 -R deploy/wiki_config/dokuwiki/data

  # Copy over the conf directory (wiki config, user data, etc)
  # This requires root
  echo "Copying ${WIKIDATA}/conf..."
  echo "This requires root permission"
  sudo cp "${WIKIDATA}/conf/"* deploy/wiki_config/dokuwiki/conf/

  # Copy over the lib directory (plugins)
  # Does not require root
  echo "Copying ${WIKIDATA}/lib..."
  cp -r "${WIKIDATA}/lib/"* deploy/wiki_config/dokuwiki/lib/
  sudo chown -R 1000:911 deploy/wiki_config/dokuwiki/lib/
}

#
# Deploy the web generator in a production environment.
#
# Set a Django secret key if needed
# Build the production docker images
# Run the production setup
#
deploy_production() {
  
  # Generate a secret key for the django config if it still contains the template text
  if grep -q "key_change_me" deploy/.env.prod; then
    echo "Generating Django secret key..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe())")
    sed -i "s/key_change_me/$SECRET_KEY/g" deploy/.env.prod
  else
    echo "Django secret key already exists.  Skipping key generation"
  fi

  # Verify the user has updated the "change_me" fields in the environment files
  if grep -q "change_me" deploy/.env.prod.db; then
    echo "Change the password in deploy/.env.prod.db and rerun."
    exit 1
  fi

  if grep -q "change_me" deploy/.env.prod.letsencrypt; then
    echo "Change the email address in deploy/.env.prod.letsencrypt and rerun."
    exit 1
  fi

  # Create volume directories needed by the containers
  mkdir deploy/wiki_config

  ln -sf "$PWD/deploy/docker-compose.prod.yml" "$COMPOSE_FILE"

  # Build and run the containers
  $DCCMD build
  $DCCMD up -d
}

#
# Deploy the staging version of the web generator.
# This uses the staging version of the letsencrypt API and does not
# include the extra sanity checks for things like passwords and keys.
#
deploy_staging() {

  if grep -q "change_me" deploy/.env.staging.letsencrypt; then
    echo "Change the email address in deploy/.env.staging.letsencrypt and rerun."
    exit 1
  fi
  # Create volume directories needed by the containers
  mkdir deploy/wiki_config

  ln -sf "$PWD/deploy/docker-compose.staging.yml" "$COMPOSE_FILE"

  # Build and run the containers
  $DCCMD build
  $DCCMD up -d
}

#
# Deploy the integration testing version of the web generator. This version runs with
# the web app and the database, like dev, but also includes the reverse proxy
# and gunicorn, like staging and prod. It does not include the wiki nor SSL
# encryption. Do not use this in a production environment.
#
# NOTE: this version will wipe existing dev or int deploys to assure
# that volumes are in a "clean/blank state" for integration testing purposes.
#
deploy_integration() {
  local yes=$1

  # check if docker-compose.yml already exists and is linked to dev or int
  if [[ -e "$COMPOSE_FILE" ]]; then
    echo "Compose file ($COMPOSE_FILE) exists."

    teardown=0
    if [[ $yes == 1 ]]; then
      teardown=1
    else
      read -p "Stop and remove containers and volumes for integration env? [y/N] " -n 1 -r
      echo
      if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        teardown=1
      fi
    fi

    if [[ $teardown == 1 ]]; then
      echo "Stopping and removing containers and volumes..."
      $DCCMD down -v
    fi
  fi

  ln -sf "$PWD/deploy/docker-compose.int.yml" "$COMPOSE_FILE"

  # Build and run the containers
  $DCCMD build
  $DCCMD up -d
}

#
# Deploy the dev version of the web generator.  This version runs with 
# just the web app and the database.  It does not include the reverse proxy,
# the wiki, or SSL encryption.  It also runs with the built-in test server
# instead of gunicorn.  Do not use this in a production environment.
#
deploy_dev() {

  ln -sf "$PWD/deploy/docker-compose.dev.yml" "$COMPOSE_FILE"

  # Build and run the containers
  $DCCMD build
  $DCCMD up -d
}

#
# Shut down the web generator.
#
shutdown() {
  echo "Shutting down..."
  $DCCMD down
}

#
# Rerun the most recent deployment
#
rerun_deployment() {
  echo "Running web generator..."
  $DCCMD up -d
}

#
# Print a usage/help message
#
print_usage() {
cat << EOF
usage deploy.sh [-p | -s | -t | -d | -r | -k | -w <path_to_wiki_backup> | -y]

  Deploy the web generator in several different configurations.

  -p: Production
      Deploy the web generator in a production environment. Performs several 
      sanity checks for passwords and keys before deploying the full web app.
  -s: Staging
      Deploy the web generator in a staging environment. Uses the staging version
      of the letsencrypt API to generate self-signed certs.
  -i: Integration
      Deploy the web generator in an integration testing environmennt.
      Closer to staging than dev but without certs or the wiki.
  -d: Development
      Deploy the web generator in a dev environment. Deploys a minimal set of containers
      to run a local dev instance.
  -k: Shutdown/kill
      Shuts down the web generator.
  -r: Rerun deployment
      Rerun the most recent config without rebuilding the containers
  -w: Wiki migration
      Takes a path to a backup of the Jets of Time wiki data and migrates it into the 
      DokuWiki container.  NOTE: This requires root.
  -y: "Yes"
      Don't prompt about warnings to destroy/remove existing containers (e.g. for testing).

EOF
}

##########
#  Main  #
##########

# Make sure we're running from the webapp/repo root.  This ensures
# all of the relative paths will be correct.
if [[ ! -f deploy/Dockerfile ]]; then
  echo "Run this script from the webapp/repository root directory."
  exit 1
fi

# Check if the jetsoftime submodule is initialized and 
# initialize/update it if it isn't.
submodule_status=$(git submodule status | grep jetsoftime)
if [[ $submodule_status =~ ^-.* ]]; then
  echo "Initializing jetsoftime submodule..."
  git submodule init
  git submodule update
fi

# Check if the Chrono Trigger ROM is present
if [[ -z "${SKIP_CTROM_CHECK:-}" ]] && [[ ! -f ct.sfc ]]; then
  echo "The Chrono Trigger ROM must be located in the webapp root and named ct.sfc"
  exit 1
fi

deploy_prod=0
deploy_staging=0
deploy_int=0
deploy_dev=0
deploy_wiki=0
shutdown=0
rerun_deployment=0
yes=0

# Figure out what type of deployment we're spinning up
while getopts 'psidkrw:y' flag
do
  case "${flag}" in
    p)
      # production deployment
      deploy_prod=1
      ;;
    s)
      # staging deployment
      deploy_staging=1
      ;;
    i)
      # integration deployment
      deploy_int=1
      ;;
    d)
      # dev deployment
      deploy_dev=1
      ;;
    k)
      # Shutdown the running deployment
      shutdown=1
      ;;
    r)
      # Rerun the most recent deployment
      rerun_deployment=1
      ;;
    w)
      # migrate wiki data to the container
      deploy_wiki=1
      wiki_data_path=${OPTARG}
      ;;
    y)
      # don't prompt
      yes=1
      ;;
    *)
      print_usage
      exit 0
    esac
done

check_and_set_env_vars

if (( deploy_prod == 1 )); then
  deploy_production
elif (( deploy_staging == 1 )); then
  deploy_staging
elif (( deploy_int == 1 )); then
  deploy_integration $yes
elif (( deploy_dev == 1 )); then
  deploy_dev
elif (( deploy_wiki == 1 )); then
  migrate_dokuwiki_data "$wiki_data_path"
elif (( shutdown == 1 )); then
  shutdown
elif (( rerun_deployment == 1 )); then
  rerun_deployment
else
  print_usage
fi

