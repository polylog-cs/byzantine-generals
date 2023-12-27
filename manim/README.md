# Manim

## Installation

```
pip3 install -r requirements.txt
# pre-commit is installed by the previous command.
pre-commit install
```

The pre-commit hooks check the code for formatting and common errors.
When the code is reformatted by the pre-commit hook, you'll have to `git add`
that file again because it has changed, and then commit.

## Usage

```
manim -pql anims.py
```