import re

from setuptools import find_namespace_packages, setup

with open("connectai/dingtalk/websocket/__init__.py") as f:
    version = re.findall("__version__.*(\d+\.\d+\.\d+).*", f.read())[0]

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="ca-dingtalk-websocket",  # package name
    version=version,  # package version
    description="dingtalk client",  # package description
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://www.connectai-e.com",
        "Code": "http://github.com/connectAI-E/Feishu-Webhook-Proxy",
        "Issue tracker": "http://github.com/connectAI-E/Feishu-Webhook-Proxy/issues",
    },
    author="lloydzhou@gmail.com",
    license="MIT",
    keywords=["Dingtalk", "Webhook", "Websocket", "Bot"],
    packages=find_namespace_packages(),
    zip_safe=False,
    install_requires=["ca-dingtalk-sdk", "websocket-client"],
    python_requires=">=3.8",
)
