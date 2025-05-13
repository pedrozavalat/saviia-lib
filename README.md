# SAVIIA Library 
*Sistema de Administración y Visualización de Información para la Investigación y Análisis*

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pedrozavalat/saviia-lib?style=for-the-badge)](https://github.com/pedrozavalat/saviia-lib/releases)


## Installation
This library is designed for use with the SAVIIA Home Assistant Integration. It provides an API to retrieve files from a THIES Data Logger via an FTP server and upload them to a Microsoft SharePoint folder using the SharePoint REST API.

```bash
pip install saviialib
```

## Usage

### Initialize the EPii API Client
To start using the library, you need to create an `EpiiAPI` client instance with its configuration class:

```python
from saviialib import EpiiAPI, EpiiAPIConfig
config = EpiiAPIConfig(
        ftp_port=FTP_PORT,
        ftp_host=FTP_HOST,
        ftp_user=FTP_USER,
        ftp_password=FTP_PASSWORD,
        sharepoint_client_id=SHAREPOINT_CLIENT_ID,
        sharepoint_client_secret=SHAREPOINT_CLIENT_SECRET,
        sharepoint_tenant_id=SHAREPOINT_TENANT_ID,
        sharepoint_tenant_name=SHAREPOINT_TENANT_NAME,
        sharepoint_site_name=SHAREPOINT_SITE_NAME
    )
api_client = EpiiAPI(config)
```
**Notes:** 
- Store sensitive data like `FTP_PASSWORD`, `FTP_USER`, and SharePoint credentials securely. Use environment variables or a secrets management tool to avoid hardcoding sensitive information in your codebase.

### Update THIES Data Logger Files
The library provides a method to synchronize THIES Data Logger files with the RCER SharePoint client. This method updates the folder containing binary files with meteorological data:

```python
from saviialib import EpiiUpdateThiesConfig
import asyncio

async def main():
    # Before calling this method, you must have initialised the api class ...
    response = await api_client.update_thies_data()
    return response

asyncio.run(main())
```

## Development

This project includes a `Makefile` to simplify common tasks. Below are the available commands:

### Install Basic Dependencies
To install the basic dependencies required for the project, run the following command:

```bash
make install-deps
```

This will ensure that all necessary libraries and tools are installed for the project to function properly.

### Install Development Requirements
For setting up a development environment with additional tools and libraries, execute:

```bash
make dev
```

This command installs all the dependencies needed for development, including testing and linting tools.

### Run Tests
To verify that the code is functioning as expected, you can run the test suite using:

```bash
make test
```

This will execute all the tests in the project and provide a summary of the results.

### Lint the Code
To ensure that the code adheres to the project's style guidelines and is free of common errors, run:

```bash
make lint
```

This command checks the codebase for linting issues and outputs any problems that need to be addressed.

## Contributing
If you're interested in contributing to this project, please follow the contributing guidelines. By contributing to this project, you agree to abide by its terms.
Contributions are welcome and appreciated!

## License

`saviialib` was created by Pedro Pablo Zavala Tejos. It is licensed under the terms of the MIT license.
