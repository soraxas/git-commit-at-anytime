import re
from os import path

from setuptools import setup

# read the contents of README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# read the version file
VERSIONFILE = "git_commit_at_anytime/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
mo = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", verstrline, re.M)
if not mo:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
version_str = mo.group(1)

setup(
    name="git-commit-at-anytime",
    version=version_str,
    description="Easily cerates git commit at desire time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tin Lai (@soraxas)",
    author_email="oscar@tinyiu.com",
    license="MIT",
    url="https://github.com/soraxas/git-commit-at-anytime",
    keywords="git commit",
    python_requires=">=3.6",
    packages=[
        "git_commit_at_anytime",
    ],
    install_requires=[
        "python-dateutil",
        "humanize",
        "pytimeparse",
        "argcomplete",
    ],
    entry_points={
        "console_scripts": [
            "git-commit-at-anytime=git_commit_at_anytime.main:run",
        ]
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Desktop Environment",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
)
