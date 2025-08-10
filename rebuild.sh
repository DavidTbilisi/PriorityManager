#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: ./build.sh [--local | --prod]"
    echo "Options:"
    echo "  --local    Build and install the package locally."
    echo "  --prod     Bump version, build, and upload the package to PyPI."
    exit 1
}

# Check if the argument is provided
if [ $# -eq 0 ]; then
    usage
fi

# Step 1: Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Handle the command-line argument
case "$1" in
    --local)
        echo "Building the package for local installation..."

        # Build the package
        python setup.py sdist bdist_wheel || { echo "Build failed"; exit 1; }

        # Check the distribution (optional)
        echo "Checking the distribution..."
        twine check dist/* || { echo "twine check failed"; exit 1; }

        # Install the package locally
        echo "Installing the package locally..."
        pip install -e . || { echo "Local installation failed"; exit 1; }
        echo "Local installation complete."
        ;;

    --prod)
        echo "Building the package for production..."

        # Step 2: Update the version in setup.py
        echo "Updating the version in setup.py..."
        bumpversion patch || { echo "bumpversion failed"; exit 1; }

        # Build the package
        python setup.py sdist bdist_wheel || { echo "Build failed"; exit 1; }

        # Check the distribution (optional)
        echo "Checking the distribution..."
        twine check dist/* || { echo "twine check failed"; exit 1; }

        # Upload to PyPI
        echo "Uploading the package to PyPI..."
        twine upload dist/* || { echo "Upload to PyPI failed"; exit 1; }
        echo "Upload to PyPI complete."
        ;;

    *)
        usage
        ;;
esac

# Display help message for the package
echo "Running 'priority_manager --help'..."
priority_manager --help
