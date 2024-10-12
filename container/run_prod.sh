#!/usr/bin/env bash

# Starts a new container based on the PROD image.
#
# Programs run as non-root-user inside the container for security reasons.

readonly local script_dir=$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" && pwd )
readonly local parent_dir=$(dirname ${script_dir})

# Container user: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
readonly local uid=1000
readonly local gid=1000

# Use --publish <host_port>:<container_port> to enable networking.
# Use --rm to remove the container after exit.
# Use --env-file "${parent_dir}/.env" to read environment variables from a file.
# Use --detach to run the container in the background.
podman container run \
    --name="$(basename ${parent_dir})_prod" \
    --pull=newer \
    --rm \
    --user ${uid}:${gid} \
    --userns keep-id:uid=${uid},gid=${gid} \
        localhost/"$(basename ${parent_dir})_prod":latest \
            "${@}"
