'''setup.py - Data - '''

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Data", 
    version="0.0.1",
    author="Adrian Spork",
    author_email="a_spor03@wwu.de",
    description="A script for downloading and preparation of Sentinel and SST Data ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeoSoftII2020-21",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='3.8.6',
)