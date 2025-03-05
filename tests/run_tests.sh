#!/usr/bin/env bash

TEST_COLLECTIONS="
.
"

TEST_MODULES="
export_dicts
"

#PYTHON_TEST_VERSION="3.9"
PYTHON_TEST_VERSION="3.10"

## ref: https://www.xmodulo.com/catch-handle-errors-bash.html
try()
{
    [[ $- = *e* ]]; SAVED_OPT_E=$?
    set +e
}

throw()
{
    exit "$1"
}

catch()
{
    export exception_code=$?
    [ "${SAVED_OPT_E}" -ne 0 ] && set +e
    return $exception_code
}


run_collection_tests() {
  TESTS=$1
  PYTHON_TEST_VERSION=$2
  COLLECTION_PATH=$3
  MODULE=$4
  TEST_RESULTS_FILE_NAME=$5

  echo "TESTS=$TESTS"
  echo "COLLECTION_PATH=$COLLECTION_PATH"
  echo "MODULE=$MODULE"

  CURRENT_DIR=${PWD}

  ## ref: https://stackoverflow.com/questions/229551/how-to-check-if-a-string-contains-a-substring-in-bash
  if [[ -d "${COLLECTION_PATH}" ]]; then
    COLLECTION_DIR=${CURRENT_DIR}/${COLLECTION_PATH}
    echo "Changing to COLLECTION_DIR=${COLLECTION_DIR}"
    cd "${COLLECTION_DIR}"
  else
    COLLECTION_DIR=${CURRENT_DIR}
    echo "Already in test COLLECTION_DIR=${COLLECTION_DIR}"
  fi

  TEST_DIR="${COLLECTION_DIR}"
  TEST_RESULTS_FILE="${CURRENT_DIR}/tests/${TEST_RESULTS_FILE_NAME}"

  # shellcheck disable=SC2194
  case "all sanity" in *"$TESTS"*)
    CMD_ANSIBLE_TEST_SANITY="ansible-test sanity -v --python ${PYTHON_TEST_VERSION} ${MODULE}"
    ;;
  esac

  # shellcheck disable=SC2194
  case "all units" in *"$TESTS"*)
    CMD_ANSIBLE_TEST_UNIT="ansible-test units -v --python ${PYTHON_TEST_VERSION} ${MODULE}"
    ;;
  esac

  # shellcheck disable=SC2194
  case "all integration" in *"$TESTS"*)
    CMD_ANSIBLE_TEST_INTEGRATION="ansible-test integration -v --python ${PYTHON_TEST_VERSION} ${MODULE}"
    ;;
  esac

  echo "TEST_DIR=$TEST_DIR"
  echo "TEST_RESULTS_FILE=$TEST_RESULTS_FILE"

  echo "*****************************" | tee -a "${TEST_RESULTS_FILE}"
  echo "Run sanity tests" | tee -a "${TEST_RESULTS_FILE}"
  echo "${CMD_ANSIBLE_TEST_SANITY}" | tee -a "${TEST_RESULTS_FILE}"
  eval "${CMD_ANSIBLE_TEST_SANITY}" | tee -a "${TEST_RESULTS_FILE}"

  echo "*****************************" | tee -a "${TEST_RESULTS_FILE}"
  echo "Run unit tests" | tee -a "${TEST_RESULTS_FILE}"
  echo "${CMD_ANSIBLE_TEST_UNIT}" | tee -a "${TEST_RESULTS_FILE}"
  eval "${CMD_ANSIBLE_TEST_UNIT}" | tee -a "${TEST_RESULTS_FILE}"

  echo "*****************************" | tee -a "${TEST_RESULTS_FILE}"
  echo "Run integration tests" | tee -a "${TEST_RESULTS_FILE}"
  echo "${CMD_ANSIBLE_TEST_INTEGRATION}" | tee -a "${TEST_RESULTS_FILE}"
  eval "${CMD_ANSIBLE_TEST_INTEGRATION}" | tee -a "${TEST_RESULTS_FILE}"

  exit ${?}
}


SCRIPT_FILE=$(basename "$0")

TESTS="${1-all}"

TEST_RESULTS_FILE_BASE="${SCRIPT_FILE%.*}"

echo "SCRIPT_FILE=${SCRIPT_FILE}"
echo "TESTS=${TESTS}"
echo "TEST_RESULTS_FILE_BASE=${TEST_RESULTS_FILE_BASE}"

#TEST_RESULTS_TIMESTAMP="$(date -Id)_$(date +%H-%M-%S)"

IFS=$'\n'
for COLLECTION_PATH in ${TEST_COLLECTIONS}
do
  COLLECTION_ID=$(basename "${COLLECTION_PATH}")
  COLLECTION_NAMESPACE=$(basename "$(dirname "${COLLECTION_PATH}")")

  COLLECTION_NAME="${COLLECTION_NAMESPACE}.${COLLECTION_ID}"

  for MODULE in ${TEST_MODULES}
  do

    #  TEST_RESULTS_FILENAME="${TEST_RESULTS_FILE_BASE}.${COLLECTION_NAME}.results.${TEST_RESULTS_TIMESTAMP}.log"
    #  TEST_RESULTS_FILENAME="${TEST_RESULTS_FILE_BASE}.${COLLECTION_NAME}.results.log"
      TEST_RESULTS_FILENAME="${TEST_RESULTS_FILE_BASE}.${COLLECTION_NAME}.${MODULE}.results.log"

      echo "COLLECTION_NAME=${COLLECTION_NAME}"
      echo "MODULE=${MODULE}"
      echo "TEST_RESULTS_FILENAME=${TEST_RESULTS_FILENAME}"

      echo "Run Collection Tests for ${COLLECTION_NAME}.${MODULE}"
      RUN_COMMAND_WITH_ARGS="run_collection_tests  ${TESTS} ${PYTHON_TEST_VERSION} ${COLLECTION_PATH} ${MODULE} ${TEST_RESULTS_FILENAME}"
      echo "${RUN_COMMAND_WITH_ARGS}"

      try
      (
        eval "${RUN_COMMAND_WITH_ARGS}"
      )
      catch || {
        export exception_code=$?
        echo "Error occurred: $exception_code"
        throw "$exception_code"    # re-throw an unhandled exception
      }

  done

done
