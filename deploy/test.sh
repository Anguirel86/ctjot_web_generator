#!/usr/bin/env bash

# This script runs integration tests against the integration testing environment
# (which is created by running: ./deploy/deploy.sh -i).
# Currently it just checks that all containers are healthy relying on their
# healthchecks defined in ./deploy/docker-compose.int.yml, although additional
# testing, e.g. with pytest/requests or otherwise, could be done in the future.

# containers to check for healthy status
CONTAINERS=(deploy-db-1 deploy-web-generator-1 nginx-proxy)

function check_all_containers_healthy() {
  all_healthy=1
  for container in "${CONTAINERS[@]}"; do
    state="$(docker inspect -f '{{ .State.Health.Status }}' "${container}" 2>&1)"
    if [[ "${state}" != "healthy" ]]; then
      echo "$container container is not healthy: ${state//[$'\r\n']}"
      all_healthy=0
    fi
  done
  return $all_healthy
}

# wait for all containers to be healthy or time out
function wait_for_healthy_containers() {
  timeout="180"
  echo "Waiting up to $timeout seconds for containers to be healthy:"
  for container in "${CONTAINERS[@]}"; do
    echo "  * $container"
  done 

  for (( i=1; i <= timeout; i++ )); do
    check_all_containers_healthy
    if [[ $? == 1 ]]; then
      echo "All containers healthy."
      exit 0
    fi
    sleep 1
  done

  echo "Some containers did not reach 'healthy' state within $timeout."
  exit 1
}

wait_for_healthy_containers
