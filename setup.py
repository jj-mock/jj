from setuptools import find_packages, setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def find_dev_required():
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


setup(
    name="jj",
    version="2.13.1",
    description="Remote HTTP Mock",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nikita Tsvetkov",
    author_email="tsv1@fastmail.com",
    python_requires=">=3.8",
    url="https://github.com/jj-mock/jj",
    project_urls={
        "Docs": "https://jj-mock.io",
        "GitHub": "https://github.com/jj-mock/jj",
    },
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"jj": ["py.typed"]},
    entry_points={
        "console_scripts": ["jj = jj._entry_point:run"]
    },
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Typing :: Typed",
    ],
)
