#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

install_requirements = [
    "nevermined-sdk-py==0.3.0",
    "web3==5.9.0",
]

# Required to run setup.py:
setup_requirements = []

test_requirements = []

dev_requirements = []

docs_requirements = []

setup(
    author="keyko-io",
    author_email="root@keyko.io",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ],
    description="🐳 Nevermined/Python pod config",
    extras_require={
        "test": test_requirements,
        "dev": dev_requirements + test_requirements + docs_requirements,
        "docs": docs_requirements,
    },
    install_requires=install_requirements,
    license="Apache Software License 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="nevermined-pod-config",
    name="nevermined-pod-config",
    packages=find_packages(),
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    url="https://github.com/keyko-io/nevermined-pod-config-py",
    version="0.1.0",
    zip_safe=False,
    entry_points={
        "console_scripts": ["pod-config=nevermined_pod_config.pod_config:main"]
    },
)