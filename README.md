# Barcode Decoder Service

## Introduction
This is the repository for the BarCode Decoder Service for the Fax as a Service (FaaS) infrastructure.
The purpose of this service is to detect barcodes present in faxes that are received by the FaaS and inject that information into the Fax Server database.

## Requirements
The installation dependencies for this project are present in the [requirements.txt](requirements.txt) file.
The development dependencies for this project are present in the [development_requirements.txt](development_requirements.txt) file.

Although all dependencies are available from [pypi](https://pypi.org/), the `pyzbar` module requires the `zbar` system library to be installed in the system.
Given that the availability of the library depends on the underlying operative system, it is necessary to check if it exists for the chosen OS.
At this moment, there is no available solution to locally build the `zbar` library from source and distribute it within the *wheel* file. This may change in the future.
For now, it is necessary to manually fulfill the requirement.

At the moment, `zbar` is available for several OSs:
* **MacOS:** `brew install zbar`
* **Debian based distros:** `apt-get install libzbar0`

## Build Artefact Procedure
### Requirement
Requires the `build` python package to be installed via `pip`
Ex: `$ pip install build`

### Building a wheel artefact
Inside the directory to where the repository was cloned, simply execute: `$ pip wheel -w ./build_dir .`
The `barcode_service` artefact will be built and droped into the `./build_dir` which will have been created by `pip` if it was not previously created.

### Defining the artefact version
By default, the artefact is built using version `99.99.99999+fffffff`
To set a different version (which is good when building an artefact for releases), update the `__version__` attribute in the [src/barcode_service/__init__.py](src/barcode_service/__init__.py) source file accordingly.
The version format must follow the [PEP 440](https://peps.python.org/pep-0440/) specification.

## Installation procedure

### From wheel artefact
Simply execute: `$ pip install <wheel artefact location>`

### From source
When inside the repository directory, simply execute `$ pip install .`

## Starting the service
Upon installation, the barcode decoder service is available in the terminal as `barcode_service`
The service has a helper which provides the CLI options which can be accessed using the flag `-h` or `--help`
Example:
```
$ barcode_service --help
usage: barcode_service [-h] [-sl SERVICE_CONFIG_LOCATION] [-ll LOG_CONFIG_LOCATION]

optional arguments:
  -h, --help            show this help message and exit
  -sl SERVICE_CONFIG_LOCATION, --service_config_location SERVICE_CONFIG_LOCATION
                        Service configuration (YAML) file path.
  -ll LOG_CONFIG_LOCATION, --log_config_location LOG_CONFIG_LOCATION
                        Log configuration (YAML) file path.
```

### Service Configuration Files
The service uses two different configuration files:
* **Execution Configuration**: This is set using the `-sl` flag. An example of this configuration can be seen in [resources/conf-sample.yaml](resources/conf-sample.yaml)
* **Logger Configuration**: This is set using the `-ll` flag. An example of this configuration can be seen in [resources/log-sample.yaml](resources/log-sample.yaml)


### Running the service using python module startup procedure
The service is implemented so that it can be launched using the python cli module startup, which is somewhat common in the python ecosystem.
For example, python provides a quick HTTP server which can be started by just calling `$ python3 -m http.server`.
In the same way, the service can be started by calling `$ python3 -m barcode_service -sl <service config file> -ll <service log config file>`


## Development
### Virtual Environment
To facilitate the development with VSCode, a local `.venv` should be created and the project dependencies should be installed in it.
The process is fairly simple. When inside the repository directory, issue the following command: `python3 -m venv --copies .venv`

### Development Install
This project was structured in a way that allows both development and execution without requiring a build + install process.
It takes leverage on the possibility of being install in [development mode (aka. editable install)](https://setuptools.pypa.io/en/latest/userguide/development_mode.html).
To facilitate the development of this project, it is also possible to install an extended version of the project which will install the development requirements.
To do so, simply install the project by issuing the command `pip install -v --editable .[dev]` in the root of the repository. Remember to check if the development virtual environment crated previously is active. A `(.venv)` indicator before the shell prompt should be visible.
Example:
```
(.venv) ┬─[cferreira@cferreira-m1:~/P/barcode]─[00:58:10]─[V:.venv]─[G:IFS-180-add-project-structure<]
╰─>$ pip install -v --editable .[dev]
```

If it is not, the virtual environment needs to be activated by using one of the following procedures (depends on the shell being used):
* **For bash:** `source ./.venv/bin/activate`
* **For fish:** `source ./.venv/bin/activate.fish`
* **For C Shell:** `source ./.venv/bin/activate.csh`


#### Running pylint
This project integrates `pylint` which allows the generation of linting reports by running `pylint ./src` in the project root directory.
`pylint` will look into the configuration set in the [pyproject.toml](pyproject.toml) file and run against all the python source code in the selected directory and subdirectorys.
In the end, a detailed report is produced which can be inspected for analysis.
`pylint` will also be used by the PyLint extension if installed. See the **VSCode** section bellow for more details.

#### Running unit tests
This project contains unit tests implemented using [pytest](https://docs.pytest.org/)
The necessary dependencies are installed when installing the project in development mode.
As so, nothing is required other than to run `pytest` on the project root directory.

Example:
```
(.venv) ┬─[cferreira@cferreira-m1:~/P/barcode]─[11:43:33]─[V:.venv]─[G:IFS-180-add-project-structure=]
╰─>$ pytest
======================================================================================================== test session starts ========================================================================================================
platform darwin -- Python 3.10.7, pytest-7.2.0, pluggy-1.0.0
rootdir: /Users/cferreira/Projects/barcode, configfile: pyproject.toml, testpaths: src/pytests
plugins: cov-4.0.0
collected 1 item

src/pytests/test_example.py .                                                                                                                                                                                                 [100%]

---------- coverage: platform darwin, python 3.10.7-final-0 ----------
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
src/barcode_service/__init__.py            3      0   100%
src/barcode_service/avroparser.py         43     28    35%   14-15, 18-21, 24-28, 34-37, 40-45, 50, 53-58
src/barcode_service/barcodemain.py        62     44    29%   21-56, 60-64, 68-79, 85-86, 90
src/barcode_service/barcodereader.py      34     24    29%   13-17, 20-27, 30-43, 49
src/barcode_service/confutil.py           49     34    31%   12-16, 19, 22, 25-26, 30-35, 38-41, 48, 53-74
src/barcode_service/eventconsumer.py      68     53    22%   16-19, 22-23, 30-44, 47-54, 57-91, 94
src/barcode_service/eventhandler.py       32     24    25%   12-19, 23-46
src/barcode_service/eventproducer.py      32     21    34%   12-21, 24-28, 31-37, 43, 46-49
src/barcode_service/faxdao.py             58     46    21%   16-22, 26-53, 56-60, 63-69, 72-76
src/barcode_service/zbarreader.py         26     18    31%   13-15, 18-34
--------------------------------------------------------------------
TOTAL                                    407    292    28%
Coverage HTML written to dir htmlcov

FAIL Required test coverage of 95% not reached. Total coverage: 28.26%

========================================================================================================= 1 passed in 0.68s =========================================================================================================
```

#### HTML Coverage report
After running `pytest`, a full coverage report will be available under the `htmlcov` directory. This will provide a highly visual state of the code coverage.
Developers are advised to check it after running the unit-tests to see the current details of the code coverage.

### Developing using VSCode

VS Code is capable of recognizing the project and selecting the virtual environment if present, when the project directory is open with it and if the [Python extension from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.python) is installed. It is advisable to use this IDE or [PyCharm from JetBrains](https://www.jetbrains.com/pycharm/).

#### Required VSCode Extensions
* [Python from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* [PyLint from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint)


#### Creating the `launch.json`
By taking leverage on the fact that this service can be started by using the python module startup, it is possible to build a simple `launch.json` configuration file which VSCode can use to start the service.
This requires the project to be installed in either production mode or development mode (check the [Development Install section](#Development-Install-section) above)

As so, just add the following information to a `launch.json` file and place it inside the `.vscode` directory present in the project root directory. If the `.vscode` directory does not exist, then it is necessary to to manually create it. VSCode will do all of this automatically when configuring the `Run & Debug` feature if requested in its Tab.
```
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Module",
            "type": "python",
            "request": "launch",
            "module": "barcode_service",
            "args": ["-sl", "conf-sample.yaml", "-ll", "log-default.yaml"],
            "cwd": "${workspaceFolder}/config_samples",
            "justMyCode": true
        }
    ]
}
```

After this is done, the service will be available in the drop-down menu at the `Run and Debug` Tab in VSCode.

#### Integrating PyTests unit tests in VSCode
By using the [Python extension from Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.python), VSCode acquires the feature to run this project unit-tests, which are implemented using the [pytest](https://docs.pytest.org/) framework.
To use that feature, it is necessary to:
* Go to the `Testing Tab` and click the `Configure Python Tests` button.
* After pressing, a selection menu will drop and ask to select what tests will be configured. All it takes is to select the `pytest framework` option.
* After the selection, a new dropdown menu will ask to `select the directory containing the tests`. Simply select `Root directory`.
This project is already configured to run `pytest` from the root directory, so all will be good.

Once this configuration is completed, the `Testing Tab`will be updated and transform into a Tree-shape Organized structure of unit tests. From here, it is possible to easily select what unit-test to run or what set of unit tests to run.
