# libdl

## todo

rename if exist

...

## Documentation

Soon™

## Installation

`pip install git+https://github.com/monolit/libdl`

or

`pip install .`

## Usage

in test*.py:
```python
from libdl import pls_run_thrgh, download


download(uri)
# or
pls_run_thrgh(uri, path="testfile", recreate=True)
# or
download(uri, filename="file", path='path')
```
