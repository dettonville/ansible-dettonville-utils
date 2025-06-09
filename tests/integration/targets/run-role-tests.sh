#!/usr/bin/env bash

#set -eux

#source virtualenv.sh

# Requirements have to be installed prior to running ansible-playbook
# because plugins and requirements are loaded before the task runs

#pip install -r requirements.txt

VERSION="2024.2.1"

PROJECT_DIR="$( git rev-parse --show-toplevel )"
#WORKDIR="${PROJECT_DIR}/.."

VAULTPASS_FILEPATH="~/.vault_pass"
if [[ -f "${PROJECT_DIR}/.vault_pass" ]]; then
  VAULTPASS_FILEPATH="${PROJECT_DIR}/.vault_pass"
fi
VAULT_FILEPATH="./../integration_config.vault.yml"
#TEST_VARS_FILE="test-vars.yml"

SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
SCRIPT_FILE=$(basename "$0")
PLAYBOOK="${SCRIPT_FILE%.*}.yml"

echo "SCRIPT_DIR=[${SCRIPT_DIR}]"
echo "SCRIPT_FILE=[${SCRIPT_FILE}]"
echo "PLAYBOOK=[${PLAYBOOK}]"
echo "PROJECT_DIR=${PROJECT_DIR}"

#export ANSIBLE_ROLES_PATH=./
export ANSIBLE_COLLECTIONS_PATH=${PROJECT_DIR}/collections
#export ANSIBLE_COLLECTIONS_PATH=${PROJECT_DIR}/collections:${WORKDIR}/requirements_collections
#export ANSIBLE_COLLECTIONS_PATH=${WORKDIR}/requirements_collections
#export ANSIBLE_DEBUG=1
export ANSIBLE_KEEP_REMOTE_FILES=1
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

function main() {

  ANSIBLE_ARGS=()
  if [ $# -gt 0 ]; then
    ANSIBLE_ARGS=("$@")
  fi

  rm -f ./ansible.log

#  execCmd="ansible-playbook "${ANSIBLE_ARGS[@]}" --vault-password-file ${VAULTPASS_FILEPATH} ${PLAYBOOK}"
  #execCmd="ansible-playbook $@ -e @${VAULT_FILEPATH} --vault-password-file ${VAULTPASS_FILEPATH} ${PLAYBOOK}"
  #execCmd="ansible-playbook $@ -e @${TEST_VARS_FILE} -e @${VAULT_FILEPATH} --vault-password-file ${VAULTPASS_FILEPATH} ${PLAYBOOK}"

  execCmd=("ansible-playbook")

  if [[ "${#ANSIBLE_ARGS[@]}" -gt 0 ]]; then
    execCmd+=("${ANSIBLE_ARGS[@]}")
  fi

  execCmd+=("--vault-password-file ${VAULTPASS_FILEPATH}")

##  VAR_GIT="--extra-vars test_component__git_test_results_enabled=false"
##  VAR_GIT="--extra-vars test_component__git_test_results_enabled=true"
#  VAR_GIT="--extra-vars 'vault_env=${VAULT_ENV},test_component__git_test_results_enabled=true'"
#  execCmd+=" ${VAR_GIT[@]}"

  execCmd+=("${PLAYBOOK}")

  echo "execCmd=${execCmd[*]}"
#  eval "${execCmd[*]}"
  ${execCmd[*]}

}

main "$@"
