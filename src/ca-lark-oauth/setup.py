import re

from setuptools import find_namespace_packages, setup

with open("connectai/lark/oauth/__init__.py") as f:
    version = re.findall("__version__.*(\d+\.\d+\.\d+).*", f.read())[0]

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="ca-lark-oauth",  # package name
    version=version,  # package version
    description="lark(feishu) oauth webhook",  # package description
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://www.connectai-e.com",
        "Code": "http://github.com/connectAI-E/connectai",
        "Issue tracker": "http://github.com/connectAI-E/connectai/issues",
    },
    author="lloydzhou@gmail.com",
    license="MIT",
    keywords=["Feishu", "Lark", "Webhook", "Oauth", "Bot"],
    packages=find_namespace_packages(),
    zip_safe=False,
    install_requires=["ca-lark-sdk", "flask"],
    python_requires=">=3.8",
    extras_require={
        "market": ["ca-lark-webhook"],
    },
)
