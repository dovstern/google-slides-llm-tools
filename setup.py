from setuptools import setup, find_packages

setup(
    name="google_slides_llm_tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "google-api-python-client",
        "langchain"
    ],
    author="LLM Developer",
    author_email="developer@example.com",
    description="A package providing tools for LLMs to interact with Google Slides",
    keywords="google-slides, langchain, llm, tools",
    url="https://github.com/yourusername/google-slides-llm-tools",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
) 