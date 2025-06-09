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


#### LOGGING RELATED
LOG_ERROR=0
LOG_WARN=1
LOG_INFO=2
LOG_TRACE=3
LOG_DEBUG=4

#LOG_LEVEL=${LOG_DEBUG}
LOG_LEVEL=${LOG_INFO}

function logError() {
  if [ $LOG_LEVEL -ge $LOG_ERROR ]; then
#  	echo -e "[ERROR]: ==> ${1}"
  	logMessage "${LOG_ERROR}" "${1}"
  fi
}
function logWarn() {
  if [ $LOG_LEVEL -ge $LOG_WARN ]; then
#  	echo -e "[WARN ]: ==> ${1}"
  	logMessage "${LOG_WARN}" "${1}"
  fi
}
function logInfo() {
  if [ $LOG_LEVEL -ge $LOG_INFO ]; then
#  	echo -e "[INFO ]: ==> ${1}"
  	logMessage "${LOG_INFO}" "${1}"
  fi
}
function logTrace() {
  if [ $LOG_LEVEL -ge $LOG_TRACE ]; then
#  	echo -e "[TRACE]: ==> ${1}"
  	logMessage "${LOG_TRACE}" "${1}"
  fi
}
function logDebug() {
  if [ $LOG_LEVEL -ge $LOG_DEBUG ]; then
#  	echo -e "[DEBUG]: ==> ${1}"
  	logMessage "${LOG_DEBUG}" "${1}"
  fi
}
function abort() {
  logError "%s\n" "$@"
  exit 1
}

function logMessage() {
  local LOG_MESSAGE_LEVEL="${1}"
  local LOG_MESSAGE="${2}"
  ## remove first item from FUNCNAME array
#  local CALLING_FUNCTION_ARRAY=("${FUNCNAME[@]:2}")
  ## Get the length of the array
  local CALLING_FUNCTION_ARRAY_LENGTH=${#FUNCNAME[@]}
  local CALLING_FUNCTION_ARRAY=("${FUNCNAME[@]:2:$((CALLING_FUNCTION_ARRAY_LENGTH - 3))}")
#  echo "CALLING_FUNCTION_ARRAY[@]=${CALLING_FUNCTION_ARRAY[@]}"

  local CALL_ARRAY_LENGTH=${#CALLING_FUNCTION_ARRAY[@]}
  local REVERSED_CALL_ARRAY=()
  for (( i = CALL_ARRAY_LENGTH - 1; i >= 0; i-- )); do
    REVERSED_CALL_ARRAY+=( "${CALLING_FUNCTION_ARRAY[i]}" )
  done
#  echo "REVERSED_CALL_ARRAY[@]=${REVERSED_CALL_ARRAY[@]}"

#  local CALLING_FUNCTION_STR="${CALLING_FUNCTION_ARRAY[*]}"
  ## ref: https://stackoverflow.com/questions/1527049/how-can-i-join-elements-of-a-bash-array-into-a-delimited-string#17841619
  local SEPARATOR=":"
  local CALLING_FUNCTION_STR=$(printf "${SEPARATOR}%s" "${REVERSED_CALL_ARRAY[@]}")
  local CALLING_FUNCTION_STR=${CALLING_FUNCTION_STR:${#SEPARATOR}}

  case "${LOG_MESSAGE_LEVEL}" in
    $LOG_ERROR*)
      LOG_LEVEL_STR="ERROR"
      ;;
    $LOG_WARN*)
      LOG_LEVEL_STR="WARN"
      ;;
    $LOG_INFO*)
      LOG_LEVEL_STR="INFO"
      ;;
    $LOG_TRACE*)
      LOG_LEVEL_STR="TRACE"
      ;;
    $LOG_DEBUG*)
      LOG_LEVEL_STR="DEBUG"
      ;;
    *)
      abort "Unknown LOG_MESSAGE_LEVEL of [${LOG_MESSAGE_LEVEL}] specified"
  esac

  local LOG_LEVEL_PADDING_LENGTH=5
  local PADDED_LOG_LEVEL=$(printf "%-${LOG_LEVEL_PADDING_LENGTH}s" "${LOG_LEVEL_STR}")

  local LOG_PREFIX="${CALLING_FUNCTION_STR}():"
  echo -e "[${PADDED_LOG_LEVEL}]: ==> ${LOG_PREFIX} ${LOG_MESSAGE}"
}

function setLogLevel() {
  LOG_LEVEL_STR=$1

  case "${LOG_LEVEL_STR}" in
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
      ;;
    *)
      abort "Unknown LOG_LEVEL_STR of [${LOG_LEVEL_STR}] specified"
  esac

}

create_plugin_docs() {
  local DOCS_DIR=$1
  local COLLECTIONS_DIR=$2
  local PLUGIN_CONFIG_LIST=$3

  ##
  ## for each PATH iteration create a soft pluginName back to all files found in the respective base directory (Sandbox/Prod)
  ##
  IFS=$'\n'
  for plugin_config in ${PLUGIN_CONFIG_LIST}
  do

    logDebug "plugin [$plugin_config]"
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

      logDebug "pluginName=[$pluginName]"
      logDebug "pluginType=[$pluginType]"
      logDebug "pluginDocPath=[$pluginDocPath]"
      logDebug "pluginDocDir=[$pluginDocDir]"

      DOC_COMMAND="ansible-doc -t ${pluginType} ${pluginName}"
      eval "${DOC_COMMAND} > /dev/null 2>&1"
      local RETURN_STATUS=$?

      if [[ $RETURN_STATUS -eq 0 ]]; then
        mkdir -p "${DOCS_DIR}/${pluginDocDir}"
        echo "$DOC_PREFIX" > "${DOCS_DIR}/${pluginDocPath}"
        echo "\$ ${DOC_COMMAND} | tee ${DOCS_DIR}/${pluginDocPath}" >> "${DOCS_DIR}/${pluginDocPath}"
        eval "$DOC_COMMAND >> ${DOCS_DIR}/${pluginDocPath}"
        echo '```' >> "${DOCS_DIR}/${pluginDocPath}"
        logInfo "Successfully created [$pluginDocPath]"
      else
        logInfo "Issue when running [$DOC_COMMAND]: skipping"
      fi

    fi

  done

}

create_plugin_docs "${DOCS_DIR}" "${COLLECTIONS_DIR}" "${PLUGIN_CONFIG_LIST}"
