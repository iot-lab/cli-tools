#! /bin/sh

test -d iotlabcli || { echo "Run the script from cli-tools root dir" ; exit 1;}

SCRIPT_DIR="$(readlink -e $(dirname $0))"
ROOT_DIR="$(readlink -e $(dirname $0)/..)"
integration_script="$(readlink -e ${SCRIPT_DIR}/test_integration.py)"

export PYTHONPATH="${ROOT_DIR}:"

python -m coverage run --source iotlabcli --omit='iotlabcli/tests/*' ${integration_script}
python -m coverage report
python -m coverage html
python -m coverage xml
