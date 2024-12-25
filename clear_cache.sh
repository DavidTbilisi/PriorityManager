find . -type d -name "__pycache__" -exec rm -r {} +
# TEST_MODE=true pytest
# TEST_MODE=true pytest -v tests/test_add.py
# TEST_MODE=true pytest -v tests/test_edit.py
