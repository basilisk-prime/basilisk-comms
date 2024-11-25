from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="basilisk-comms",
    version="0.1.0",
    author="B4S1L1SK_PR1M3",
    author_email="B4S1L1SK.PR1M3@gmail.com",
    description="Secure communication framework for digital liberation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B4S1L1SK-PR1M3/basilisk-comms",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
)