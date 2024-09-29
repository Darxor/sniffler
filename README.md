# Sniffler

Sniff out stuff about your files.

## Installation

### With [rye](https://rye.astral.sh/)

```bash
rye init . --virtual
rye sync --no-dev
```

### With [pip]

Suggested to use a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

```bash
pip install -r requirements.lock
pip install .
```

## Usage

```bash
> sniffler -h
usage: sniffler [-h] [-O OUTPUT] path

Collect information about files in a directory.

positional arguments:
  path                  The path to the directory to collect information from.

options:
  -h, --help            show this help message and exit
  -O OUTPUT, --output OUTPUT
                        The path to the output file.
```

This will collect information about the files in the current directory and output it to `output.tsv`.
```bash
sniffler . -O output.tsv
```