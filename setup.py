import subprocess
from setuptools import setup

# from test_git import GetGitVersion as gv
# Obtain the short Git commit hash
commit_hash = (
    subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
    .strip()
    .decode("utf-8")
)

setup(
    name="libdl",
    version="1.1+" + commit_hash,
    description="library-download",
    url="https://github.com/monolit/libdl",
    author="monolit_01",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    py_modules=["libdl"],
    install_requires=[
        "requests",
        "tqdm",
        "datetime",
    ],
    entry_points={
        "console_scripts": ["libdl=libdl:pls_run_thrgh"],
    },
)
