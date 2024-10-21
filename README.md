# Sniffler

Sniff out stuff about your files.

## Installation

### With [rye](https://rye.astral.sh/)

```bash
rye init . --virtual
rye sync --no-dev
```

### With pip

Suggested to use a [virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

```bash
pip install -r requirements.lock
pip install .
```

## Usage

```bash
> sniffler -h
usage: sniffler [-h] [-O OUTPUT] [--delimiter DELIMITER] path

Collect information about files in a directory.

positional arguments:
  path                  The path to the directory to collect information from.

options:
  -h, --help            show this help message and exit
  -O OUTPUT, --output OUTPUT
                        The path to the output file.
  --delimiter DELIMITER
                        The delimiter to use in the output file (',', ';', or 'tab').
```

Alternatively, you can run `src/sniffler` directly.
```bash
python src/sniffler -h
```

This will collect information about the files in the current directory and output it to `output.csv`.
```bash
sniffler . -O output.csv
```

Note: When no output file is specified, the output will be printed to the console as a CSV.