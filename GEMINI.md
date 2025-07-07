
# Gemini Code Working Guide: platformio-fixed

This document provides an AI-centric overview of the `platformio-core` repository, designed to guide generative AI agents in understanding, navigating, and contributing to the project.

## Project Overview

`platformio-core` is the command-line interface (CLI) for the PlatformIO ecosystem, an open-source platform for embedded systems development. It provides a rich set of features for managing projects, libraries, and development boards, as well as for building, testing, and debugging embedded applications.

## Codebase Structure

The repository is organized into several key directories, each with a specific purpose:

- **`platformio`**: The main source code for the `platformio-core` CLI. It is a Python package with a modular structure, where each subdirectory corresponds to a specific feature or component of the PlatformIO ecosystem.
- **`tests`**: Contains the test suite for the project. The directory structure mirrors that of the `platformio` directory, with dedicated tests for each component. The tests are written using the `pytest` framework.
- **`docs`**: Contains the documentation for the project, written in reStructuredText.
- **`examples`**: Contains example projects that demonstrate how to use PlatformIO for various development boards and frameworks.
- **`scripts`**: Contains various scripts for automating tasks such as documentation generation and installation of development platforms.

## Key Files

- **`setup.py`**: The main entry point for the project's packaging and distribution. It defines the project's metadata, dependencies, and entry points for the CLI.
- **`platformio/__main__.py`**: The main entry point for the `platformio` command-line interface. It is responsible for parsing command-line arguments and dispatching them to the appropriate handlers.
- **`platformio/cli.py`**: Defines the command-line interface for the `platformio` command. It uses the `click` library to create a user-friendly CLI with support for commands, options, and arguments.
- **`platformio/project/config.py`**: Handles the parsing and validation of the `platformio.ini` configuration file, which is the central configuration file for PlatformIO projects.
- **`tests/conftest.py`**: Contains pytest fixtures and other test-related configurations.

## Development Workflow

The project uses a standard Python development workflow, with the following key steps:

1.  **Installation**: The project can be installed from PyPI using `pip install platformio`. For development, it is recommended to install it in editable mode using `pip install -e .`.
2.  **Testing**: The test suite can be run using the `pytest` command. The tests are organized into subdirectories that mirror the structure of the `platformio` directory.
3.  **Linting**: The project uses `pylint` for code linting. The configuration is defined in the `.pylintrc` file.
4.  **Continuous Integration**: The project uses GitHub Actions for continuous integration. The workflows are defined in the `.github/workflows` directory.

## How to Contribute

To contribute to the project, follow these steps:

1.  Fork the repository on GitHub.
2.  Create a new branch for your changes.
3.  Make your changes and add tests for them.
4.  Run the test suite to ensure that your changes do not break any existing functionality.
5.  Submit a pull request with a clear description of your changes.
