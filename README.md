# RCER IoT Client Library | `rcer_iot_client_pkg`


## Installation
You can find the package on [PyPI](https://pypi.org/project/rcer-iot-client-pkg/). 
This library provides a robust and efficient client for interacting with IoT devices.

```bash
pip install rcer_iot_client_pkg
```

## Usage

### Initialize the EPii API Client
To start using the library, you need to create an `EpiiAPI` client instance:

```python
from rcer_iot_client_pkg import EpiiAPI

api_client = EpiiAPI()
```

### Update THIES Data Logger Files
The library provides a method to synchronize THIES Data Logger files with the RCER SharePoint client. This method updates the folder containing binary files with meteorological data:

```python
import asyncio

async def update_thies_data():
    response = await api_client.update_thies_data(
        ftp_port=PORT,
        ftp_host=LOCAL_HOST,
        ftp_password=PASSWORD,
        ftp_user=USER
    )
    return response

asyncio.run(update_thies_data())
```

**Notes:** 
- Store sensitive data like `PASSWORD` and `USER` securely, e.g., in environment variables or a secrets file.
- Ensure `asyncio` is installed to run concurrent code with `EpiiAPI` methods.

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
If you're interested in contributing to this project, please follow the contributing guidelines. Contributions are welcome and appreciated!

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`rcer_iot_client_pkg` was created by Pedro Pablo Zavala Tejos. It is licensed under the terms of the MIT license.
