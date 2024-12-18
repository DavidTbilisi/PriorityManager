# Step 1: Update the version in setup.py

# Step 2: Clean previous builds
rm -rf dist/ build/ *.egg-info

# Step 3: Build the package
python3 setup.py sdist bdist_wheel

# Step 4: Check the distribution (optional)
# twine check dist/*

# Step 5: Upload to PyPI
# twine upload dist/*

# For Test PyPI
# twine upload --repository testpypi dist/*


# Install the package locally
pip install -e .

# Execute 
priority_manager --help