#!/usr/bin/env python
"""
Installs FiftyOne Docs Search.
| Copyright 2017-2023, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    "argcomplete",
    "google-cloud-storage",
    "markdownify",
    "openai",
    "packaging",
    "qdrant-client",
    "regex",
    "rich",
    "setuptools",
    "tqdm",
]
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setup(
    name="fiftyone-docs-search",
    version="0.20.1",
    author="Voxel51, Inc.",
    author_email="info@voxel51.com",
    packages=find_packages(),
    description="Semantic search for the FiftyOne Docs from command line",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/voxel51/fiftyone-docs-search",
    license='Apache',
    python_requires='>=3.8',
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={"console_scripts": ["fiftyone-docs-search=fiftyone.docs_search.cli:main"]},
)
