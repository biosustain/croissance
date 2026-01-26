# Workflows

## cicd

Basic continuous integration and deployment (CI/CD) workflow for Python packages.

- checks formatting (black, isort)
- checks linting (ruff)
- run unit tests (pytest)
- optional: add c extensions to a package
- if all checks pass, build and deploy to PyPI if `tag` triggered the workflow
