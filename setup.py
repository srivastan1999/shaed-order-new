"""
Setup configuration for SHAED Order ELT
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="shaed-order-elt",
    version="1.0.0",
    description="SHAED Order ELT - Extract, Load, Transform pipeline for orders and Ford dealer data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SHAED",
    packages=find_packages(exclude=["tests", "backend", "data", "config"]),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "shaed-elt=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

