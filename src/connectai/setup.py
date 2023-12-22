import re

from setuptools import find_packages, setup

with open("connectai/__init__.py") as f:
    version = re.findall("__version__.*(\d+\.\d+\.\d+).*", f.read())[0]

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="connectai",  # package name
    version=version,  # package version
    description="lark(feishu) client",  # package description
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://www.connectai-e.com",
        "Code": "http://github.com/connectAI-E/connectai",
        "Issue tracker": "http://github.com/connectAI-E/connectai/issues",
    },
    author="lloydzhou@gmail.com",
    license="MIT",
    keywords=["Feishu", "Lark", "Webhook", "Websocket", "Bot"],
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "ca-lark-sdk",
        "ca-lark-websocket",
        "ca-lark-webhook",
        "flask",
        "python-dotenv",
    ],
    python_requires=">=3.8",
    extras_require={
        "langchain": ["langchain"],
        "dingtalk": [
            "ca-dingtalk-sdk",
            "ca-dingtalk-websocket",
            "ca-dingtalk-webhook",
        ],
        "lark-helper": ["ca-lark-helper"],
        "dingtalk-helper": ["ca-dingtalk-helper"],
    },
)
