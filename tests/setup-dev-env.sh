#!/usr/bin/env bash

COLLECTION_NAMESPACE="dettonville"
COLLECTION_NAME="utils"

PROJECT_DIR="$( git rev-parse --show-toplevel )"
COLLECTION_SOURCE_DIR="$( basename "${PROJECT_DIR}" )"
WORKDIR="$(cd "${PROJECT_DIR}/.." && pwd)"
COLLECTION_DIR="${WORKDIR}/requirements_collections/ansible_collections/${COLLECTION_NAMESPACE}"

mkdir -p "${COLLECTION_DIR}"
cd "${COLLECTION_DIR}" || (echo "unable to cd to ${COLLECTION_DIR}" && exit 1)
ln -s "../../../${COLLECTION_SOURCE_DIR}" "${COLLECTION_NAME}"
