#! /bin/bash
set -e
echo "n\n\n\n"
echo "========= STEP - Prep Deploy to PyPI ========="
# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Set TWINE_PASSWORD based on IS_TEST_PYPI
echo "STEP - IS_TEST_PYPI: $IS_TEST_PYPI"
if [ "$IS_TEST_PYPI" = "true" ]; then
    echo "Deploying to Test PyPI"
    export TWINE_PASSWORD="$TWINE_PASSWORD_TEST"
    PYPI_REPO="--repository testpypi"
else
    echo "Deploying to Production PyPI"
    export TWINE_PASSWORD="$TWINE_PASSWORD_PROD"
    PYPI_REPO=""
fi

# Check if TWINE_PASSWORD is set
if [ -z "$TWINE_PASSWORD" ]; then
    echo "Error: TWINE_PASSWORD environment variable is not set"
    exit 1
fi

echo "STEP - Increment version number in pyproject.toml"
# Increment version number in pyproject.toml
CURRENT_VERSION=$(grep -m 1 'version = "[0-9]*\.[0-9]*\.[0-9]*"' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $CURRENT_VERSION"
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
echo "New version: $NEW_VERSION"
sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
rm -f pyproject.toml.bak

echo "STEP - Remove previous build files"
# remove previous build files (from the current directory 'pip_package')
rm -rf dist/

echo "STEP - Build the package"
# build the package
python -m build

echo "STEP - Check .whl file is valid after build"
# check .whl file is valid after build
twine check dist/*

echo "STEP - Upload to PyPI"
# Prompt user for confirmation before upload
echo "IS_TEST_PYPI: $IS_TEST_PYPI"
read -p "Ready to upload to PyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Upload cancelled"
    exit 1
fi

# upload to PyPI (test or production based on IS_TEST_PYPI)
export TWINE_USERNAME="__token__"
twine upload $PYPI_REPO dist/*

# === EXTRA ===
# make sure python pip build modules are installed
#pip install build twine hatchling

# install locally built module to test
#pip install dist/langchain_tableau-$NEW_VERSION-py3-none-any.whl --force-reinstall

# install package in debug mode. This will allow us to reference tableau_langchain from other folders in the project
# cd pkg
# pip install -e .

# pip install from PyPI Test
# pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ langchain-tableau

# pip install from PyPI Prod
# pip install langchain-tableau

