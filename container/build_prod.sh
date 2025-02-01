#!/usr/bin/env bash

# Builds a new PROD container image
#
# TODO: Update BASE_IMAGE when a new Debian stable gets released.
#
# * https://hub.docker.com/_/debian
# * https://github.com/debuerreotype/docker-debian-artifacts
# * https://github.com/docker-library/official-images

readonly local base_image=docker.io/library/debian:bookworm-slim
readonly local script_dir=$( cd "$( dirname "${BASH_SOURCE[0]:-${(%):-%x}}" )" && pwd )
readonly local parent_dir=$(dirname ${script_dir})

# Use --no-cache if you want to build a fresh container.
# Use --target=stageName to stop the build at a specific stage.
# Use --build-arg=arg=value to pass variable values to the Containerfile
# NOTE: `latest` tags do always trigger auto-pull.
# Use --pull=always to do this also for images without `latest` tags.
# NOTE: We use cache dirs to speed up the build process. Named volumes not
# supported during build, only bind-mounts are. We mount at /root to workaround
# a non-root user issue, see Containerfile > USER root.
# TODO: Use container build cache instead of bind mounts?
podman image build \
    --build-arg=BASE_IMAGE="${base_image}" \
    --file="${script_dir}/Containerfile" \
    --ignorefile="${script_dir}/Containerignore_prod" \
    --no-cache \
    --pull=always \
    --tag="$(basename ${parent_dir})_prod":"$(date --iso-8601)" \
    --tag="$(basename ${parent_dir})_prod":latest \
    --target=prod \
    --volume "${HOME}/.cache/huggingface:/root/.cache/huggingface:z,rw" \
    --volume "${HOME}/.cache/pre-commit:/root/.cache/pre-commit:z,rw" \
    --volume "${HOME}/.cache/rattler:/root/.cache/rattler:z,rw" \
    --volume "${HOME}/.cargo:/root/.cargo:z,rw" \
    --volume "${HOME}/.pixi:/root/.pixi:z,rw" \
    --volume "${HOME}/.rustup:/root/.rustup:z,rw" \
        "${parent_dir}"
