from setuptools import setup, find_packages
import os

# Read the contents of README.md
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="priority_manager",
    version="0.1.6",
    description="A CLI tool for managing tasks with priorities and statuses.",
    long_description=long_description,  # Add the long description
    long_description_content_type="text/markdown",  # Specify the format of README.md
    url="https://github.com/DavidTbilisi/PriorityManager",
    author="David Chincharashvili",
    author_email="davidchincharashvili@gmail.com",
    packages=find_packages(),
    install_requires=[
        "click",
        "PyYAML"
    ],
    entry_points={
        "console_scripts": [
            "priority-manager=priority_manager.main:cli"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
