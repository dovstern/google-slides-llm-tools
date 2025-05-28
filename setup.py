from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies required for the main functionality
core_requirements = [
    "google-auth>=2.22.0",
    "google-auth-oauthlib>=1.0.0", 
    "google-api-python-client>=2.90.0",
    "langchain>=0.3.20",
    "langchain-openai>=0.0.2",
    "mcp>=0.1.0",
    "pydantic>=2.0.0",
    "tenacity>=8.2.2",
    "requests>=2.31.0",
    "pillow>=10.0.0",
    "PyPDF2>=3.0.0",
    "langchain-tool-to-mcp-adapter>=0.1.4",
]

# Ensure bin directory exists
if not os.path.exists('bin'):
    os.makedirs('bin')

setup(
    name="google-slides-llm-tools",
    version="0.2.3",
    author="Dov Stern",
    author_email="dstern215@gmail.com",
    description="Tools for LLMs to interact with Google Slides",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dovstern/google-slides-llm-tools",
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
    install_requires=core_requirements,
    extras_require={
        "examples": ["langgraph"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
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