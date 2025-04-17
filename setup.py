from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

# Ensure bin directory exists
if not os.path.exists('bin'):
    os.makedirs('bin')

setup(
    name="google-slides-llm-tools",
    version="0.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Tools for LLMs to interact with Google Slides",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/google-slides-llm-tools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    scripts=["bin/google_slides_mcp.py"],
    include_package_data=True,
    package_data={
        "": ["bin/*"],
    },
    entry_points={
        "console_scripts": [
            "google-slides-mcp=google_slides_llm_tools.mcp_server:main",
        ],
    },
) 