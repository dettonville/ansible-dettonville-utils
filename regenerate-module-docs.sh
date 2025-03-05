#!/usr/bin/env bash

PROJECT_DIR=$( git rev-parse --show-toplevel )
COLLECTIONS_DIR="${PROJECT_DIR}/."
DOCS_DIR="${PROJECT_DIR}/docs/plugins"

#echo "SCRIPT_DIR=${SCRIPT_DIR}"
echo "PROJECT_DIR=${PROJECT_DIR}"
echo "DOCS_DIR=${DOCS_DIR}"

## For `PLUGIN_CONFIG_LIST` use the following format to specify any special pluginNames
## [plugin_name]:[plugin_type]
##

#PLUGIN_CONFIG_LIST=""
PLUGIN_CONFIG_LIST=$((find . -type f -wholename "*/plugins/modules/*.py" \
  | sed 's|./||' \
  | sed 's|\(.*\)/\(.*\)/\(.*\)/\(.*\)/\(.*\).py|\1.\2.\5:module|' &&
  find . -type f -wholename "*/plugins/lookup/*.py" \
  | sed 's|./||' \
  | sed 's|\(.*\)/\(.*\)/\(.*\)/\(.*\)/\(.*\).py|\1.\2.\5:lookup|' &&
  find . -type f -wholename "*/plugins/filter/*.py" \
  | sed 's|./||' \
  | sed 's|\(.*\)/\(.*\)/\(.*\)/\(.*\)/\(.*\).py|\1.\2.\5:filter|') \
  | sort)

#echo "PLUGIN_CONFIG_LIST=${PLUGIN_CONFIG_LIST}"

DOC_PREFIX='

```shell
$ ansible --version
ansible [core 2.16.2]
  config file = /Users/ljohnson/repos/ansible/ansible_collections/dettonville.utils/ansible.cfg
  configured module search path = ['/Users/ljohnson/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/ljohnson/.pyenv/versions/3.11.6/lib/python3.11/site-packages/ansible
  ansible collection location = /Users/ljohnson/.ansible/collections:/usr/share/ansible/collections:/Users/ljohnson/repos/ansible/ansible_collections/dettonville.utils/collections
  executable location = /Users/ljohnson/.pyenv/versions/3.11.6/bin/ansible
  python version = 3.11.6 (main, Jan 18 2024, 13:13:46) [Clang 15.0.0 (clang-1500.0.40.1)] (/Users/ljohnson/.pyenv/versions/3.11.6/bin/python3.11)
  jinja version = 3.1.3
  libyaml = True
$
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ cd ${PROJECT_DIR}
$'

echo "DOC_PREFIX=${DOC_PREFIX}"


LOG_ERROR=0
LOG_WARN=1
LOG_INFO=2
LOG_TRACE=3
LOG_DEBUG=4

#LOG_LEVEL=${LOG_DEBUG}
LOG_LEVEL=${LOG_INFO}

function logError() {
  if [ $LOG_LEVEL -ge $LOG_ERROR ]; then
  	echo -e "[ERROR]: ${1}"
  fi
}
function logWarn() {
  if [ $LOG_LEVEL -ge $LOG_WARN ]; then
  	echo -e "[WARN ]: ${1}"
  fi
}
function logInfo() {
  if [ $LOG_LEVEL -ge $LOG_INFO ]; then
  	echo -e "[INFO ]: ${1}"
  fi
}
function logTrace() {
  if [ $LOG_LEVEL -ge $LOG_TRACE ]; then
  	echo -e "[TRACE]: ${1}"
  fi
}
function logDebug() {
  if [ $LOG_LEVEL -ge $LOG_DEBUG ]; then
  	echo -e "[DEBUG]: ${1}"
  fi
}

function setLogLevel() {
  local LOGLEVEL=$1

  case "${LOGLEVEL}" in
    ERROR*)
      LOG_LEVEL=$LOG_ERROR
      ;;
    WARN*)
      LOG_LEVEL=$LOG_WARN
      ;;
    INFO*)
      LOG_LEVEL=$LOG_INFO
      ;;
    TRACE*)
      LOG_LEVEL=$LOG_TRACE
      ;;
    DEBUG*)
      LOG_LEVEL=$LOG_DEBUG
      ALWAYS_SHOW_TEST_RESULTS=1
      ;;
    *)
      abort "Unknown loglevel of [${LOGLEVEL}] specified"
  esac

}

create_plugin_docs() {
  local DOCS_DIR=$1
  local COLLECTIONS_DIR=$2
  local PLUGIN_CONFIG_LIST=$3
  local LOG_PREFIX="==> create_plugin_docs():"

  ##
  ## for each PATH iteration create a soft pluginName back to all files found in the respective base directory (Sandbox/Prod)
  ##
  IFS=$'\n'
  for plugin_config in ${PLUGIN_CONFIG_LIST}
  do

    logDebug "${LOG_PREFIX} plugin [$plugin_config]"
    # split sub-list if available
    if [[ $plugin_config == *":"* ]]
    then
      # ref: https://stackoverflow.com/questions/12317483/array-of-arrays-in-bash
      # split server name from sub-list
#      pluginConfigArray=(${plugin_config//:/})
      IFS=":" read -a pluginConfigArray <<< $plugin_config
      pluginName=${pluginConfigArray[0]}
      pluginType=${pluginConfigArray[1]}

      pluginDocPath="${pluginName//\.//}.md"
      pluginDocDir=$(dirname "${pluginDocPath}")

      logDebug "${LOG_PREFIX} pluginName=[$pluginName]"
      logDebug "${LOG_PREFIX} pluginType=[$pluginType]"
      logDebug "${LOG_PREFIX} pluginDocPath=[$pluginDocPath]"
      logDebug "${LOG_PREFIX} pluginDocDir=[$pluginDocDir]"

      DOC_COMMAND="ansible-doc -t ${pluginType} ${pluginName}"
      eval "${DOC_COMMAND} > /dev/null 2>&1"
      local RETURN_STATUS=$?

      if [[ $RETURN_STATUS -eq 0 ]]; then
        mkdir -p "${DOCS_DIR}/${pluginDocDir}"
        echo "$DOC_PREFIX" > "${DOCS_DIR}/${pluginDocPath}"
        echo "\$ ${DOC_COMMAND} | tee ${DOCS_DIR}/${pluginDocPath}" >> "${DOCS_DIR}/${pluginDocPath}"
        eval "$DOC_COMMAND >> ${DOCS_DIR}/${pluginDocPath}"
        echo '```' >> "${DOCS_DIR}/${pluginDocPath}"
        logInfo "${LOG_PREFIX} Successfully created [$pluginDocPath]"
      else
        logInfo "${LOG_PREFIX} Issue when running [$DOC_COMMAND]: skipping"
      fi

    fi

  done

}

create_plugin_docs "${DOCS_DIR}" "${COLLECTIONS_DIR}" "${PLUGIN_CONFIG_LIST}"
