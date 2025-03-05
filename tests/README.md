
# Testing Modules

## Test environment

```shell
$ export TEST_PYTHON_VERSION="3.10"
$ export ANSIBLE_KEEP_REMOTE_FILES=1
$ export ANSIBLE_DEBUG=1
$ PROJECT_DIR="$( git rev-parse --show-toplevel )"
$ COLLECTION_DIR=${PROJECT_DIR}/collections/ansible_collections/dettonville/utils
$ echo "COLLECTION_DIR=${COLLECTION_DIR}"
$ cd ${COLLECTION_DIR}
```

### Testing

### Run All Tests

```shell
tests/run_tests.sh > run_test.results.txt

```

### Run Individually

## Sanity Testing

```shell
ansible-test sanity -v --docker --python ${TEST_PYTHON_VERSION} export_dicts

```

## Integration Testing

```shell
ansible-test integration export_dicts

```
