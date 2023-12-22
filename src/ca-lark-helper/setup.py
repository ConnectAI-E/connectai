from setuptools import find_namespace_packages, setup

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="ca-lark-helper",  # package name
    version=get_version("connectai/lark/helper/__init__.py"),  # package version
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
    packages=find_namespace_packages(),
    zip_safe=False,
    install_requires=["ca-lark-websocket", "ca-lark-sdk", "httpx"],
    python_requires=">=3.8",
)
