from setuptools import setup, find_packages


setup(
    name="jj",
    version="2.0.0-dev.3",
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nikita Tsvetkov",
    author_email="nikitanovosibirsk@yandex.com",
    python_requires=">=3.6.0",
    url="https://github.com/nikitanovosibirsk/jj",
    license="Apache 2",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "aiohttp==3.5.4",
        "undecorated==0.3.0",
    ],
    setup_requires=["pytest-runner"],
    tests_require=[
        "asynctest==0.12.2",
        "mypy==0.670",
        "flake8==3.7.7",
        "coverage==4.5.2",
        "codecov==2.0.15",
        "pytest==4.4.1",
        "pytest-asyncio==0.10.0",
        "pytest-cov==2.6.1",
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
