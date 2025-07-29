#!/usr/bin/env python3
"""
Setup script for Rush Gaming Competitive Intelligence System
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="rush-ci",
    version="1.0.0",
    author="Rush Gaming CI Team",
    author_email="ci-team@rushgaming.com",
    description="Automated competitive intelligence system for Rush Gaming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rushgaming/rush-ci",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.12",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "feedparser>=6.0.10",
        "pandas>=2.1.4",
        "python-dotenv>=1.0.0",
        "python-twitter-v2>=0.7.8",
        "linkedin-api>=2.0.0",
        "selenium>=4.15.2",
        "openai>=1.3.7",
        "spacy>=3.7.2",
        "nltk>=3.8.1",
        "airtable-python-wrapper>=0.15.3",
        "notion-client>=2.2.1",
        "redis>=5.0.1",
        "slack-sdk>=3.26.1",
        "boto3>=1.34.0",
        "schedule>=1.2.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "lxml>=4.9.3",
        "html5lib>=1.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "rush-ci=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rush_ci": ["config/*.json"],
    },
    keywords="competitive intelligence, gaming, automation, monitoring, analysis",
    project_urls={
        "Bug Reports": "https://github.com/rushgaming/rush-ci/issues",
        "Source": "https://github.com/rushgaming/rush-ci",
        "Documentation": "https://github.com/rushgaming/rush-ci/blob/main/README.md",
    },
) 