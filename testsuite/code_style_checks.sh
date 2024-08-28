#!/bin/sh

cd /src/
PYTHON_FILES_TO_CHECK=`ls | grep '.py$'`
if [[ "$PYTHON_FILES_TO_CHECK" == "" ]]
then
    echo "INFO: No .py files changed in the git commit, not running any code quality checks"
    exit 0
fi

echo "INFO: .py files that changed, and those that will be checked are: $PYTHON_FILES_TO_CHECK"

echo "INFO: Running pylint"
time pylint -j 0 $PYTHON_FILES_TO_CHECK
if [[ $? -ne 0 ]]
then
    echo "ERROR: pylint checks failed, see above for details. Please fix and commit again"
    exit 1
fi

echo "INFO: Running pycodestyle"
time pycodestyle --ignore=E501 $PYTHON_FILES_TO_CHECK
if [[ $? -ne 0 ]]
then
    echo "ERROR: pycodestyle checks failed, see above for details. Please fix and commit again"
    exit 1
fi
echo "INFO: Running pep257"
time pep257 $PYTHON_FILES_TO_CHECK --explain --source --count
if [[ $? -ne 0 ]]
then
    echo "ERROR: pep257 checks failed, see above for details. Please fix and commit again"
    exit 1
fi
