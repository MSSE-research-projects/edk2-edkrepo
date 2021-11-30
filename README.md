Public fork for purposes of project Refactoring to Remove Technical Debt at Carnegie Mellon University - Silicon Valley.

This fork contains two extra branches: before-refactoring and after-refactoring. Both branches reflect the state of the codebase immediately before and after my commits where I performed the refactoring operations. The main difference will be in /edkrepo/commands/f2f_cherry_pick_command.py.

Refactoring operations:

1. Extract Function
  * Source element: f2f_cherry_pick_command.py:99-106
  * Target element: f2f_cherry_pick_command.py:118-126
  * Rationale: Previously, the main function in the script was extremely long and monolithic. Multiple Extract Method operations were performed to logically modularize sections of the script to improve readability and maintainability.

2. Extract Function
  * Source element: f2f_cherry_pick_command.py:107-120
  * Target element: f2f_cherry_pick_command.py:128-151
  * Rationale: Previously, the main function in the script was extremely long and monolithic. Multiple Extract Method operations were performed to logically modularize sections of the script to improve readability and maintainability.

3. Extract Function
  * Source element: f2f_cherry_pick_command.py:121-133
  * Target element: f2f_cherry_pick_command.py:153-164
  * Rationale: Previously, the main function in the script was extremely long and monolithic. Multiple Extract Method operations were performed to logically modularize sections of the script to improve readability and maintainability.

4. Extract Function
  * Source element: f2f_cherry_pick_command.py:134-176
  * Target element: f2f_cherry_pick_command.py:166-210
  * Rationale: Previously, the main function in the script was extremely long and monolithic. Multiple Extract Method operations were performed to logically modularize sections of the script to improve readability and maintainability.

5. Extract Function
  * Source element: f2f_cherry_pick_command.py:177-314
  * Target element: f2f_cherry_pick_command.py:212-360
  * Rationale: Previously, the main function in the script was extremely long and monolithic. Multiple Extract Method operations were performed to logically modularize sections of the script to improve readability and maintainability.

6. Consolidate Redundant Conditional Statements
  * Source element: f2f_cherry_pick_command.py:107-175
  * Target element: f2f_cherry_pick_command.py:102-112, 128-210
  * Rationale: There were instances where the same conditional check was being performed multiple times consecutively, with no changes to any local variables in between. It was logical to combine them so that we are not making redundant checks. This went hand-in-hand with the Extract Function operations above, such that I could perform one check at the top, and call the proper extracted methods accordingly.

7. Introduce Parameter Object 
  * Source element: --
  * Target element: RepoInfo, CommitInfo, CherryPickInfo
  * Smell: Long Parameter List
  * During the above Extract Function operations, there were many local variables in the original method that made refactoring quite tough. The new functions had signatures with many parameters, and returned many variables as well. This was far too complex, and severely decreased the readability of the script. As a result, we performed the Introduce Parameter Object and divided the local variables into 3 distinct Python namedtuples. This helped clean up all of the function signatures and return values and make the code much more readable.


# EdkRepo - The Multi-Repository Tool for EDK II

# Introduction

EdkRepo is the multi-repository tool for EDK II firmware development. EdkRepo is built on top of git. It is intended to automate common developer workflows for projects that use more than one git repository. For example many of the new projects in the edk2-platforms repository require the user to clone several git repositories. EdkRepo makes it easier to set up and upstream changes for these projects. EdkRepo does not replace git, rather it provides higher level extensions that make it easier to work with git. EdkRepo is written in Python and is compatible with Python 3.5 or later.

# Build and Installation
## Linux Instructions
### Pre-Requisites
- Git 2.13.x or later
- Python 3.5 or later
- Python SetupTools
- Python Pip
### Ubuntu Specific Instructions
Tested versions: 20.04 LTS, 18.04 LTS, 16.04 LTS
#### Install Dependencies (Ubuntu 20.04, 18.04, 16.04)
`sudo apt-get install git python3 python3-setuptools python3-pip`
#### Upgrade git (Ubuntu 16.04 LTS Only)
The version of git that is installed by default in Ubuntu 16.04 is too old for EdkRepo (16.04 includes git 2.7.4, the minimum is 2.13+). To upgrade git, run the following commands:

`sudo apt-add-repository ppa:git-core/ppa`

Press [ENTER] to confirm that you want to add the new repository.

`sudo apt-get update`

`sudo apt-get install git`

### OpenSUSE
`sudo zipper install git python3 python3-setuptools python3-pip`

### Install Process
Installing EdkRepo on Linux requires one to extract the tarball and run the included installer script.
1. Extract the archive using the following command
  `tar -xzvf edkrepo-<version>.tar.gz`
2. Run the installer script with elevated privileges
  `sudo ./install.py --user <username>`

The -v flag can be added for more verbose output if desired.

### Build Process
To build a EdkRepo distribution tarball, the Python wheel package is required in addition to the above dependencies. On Ubuntu, one can install it using:

`sudo apt-get install python3-wheel`

1. `cd build-scripts`
2. `./build_linux_installer.py`

### Install From Source
To install from source, one must have installed using the tarball method above at least once in order to setup the EdkRepo configuration files. One this is done, one may use the standard distutils method to install EdkRepo from source:

`./setup.py install`

## macOS Instructions

### Install Pre-Requisites

#### 1. Install the Xcode Command Line Tools

a) Open a Terminal and type the following command:

`xcode-select --install`

b) A new window will appear, click Install.
c) Accept the license agreement.
d) Wait for the installation to complete.

#### 2. Install Homebrew

Install [Homebrew](https://brew.sh/) if it has not been installed already. Homebrew is a package manager for macOS that has become the most common method of installing command line software on macOS that was not originally provided by Apple. EdkRepo has several dependencies that are distributed via Homebrew.

Type the following command to install Homebrew:

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`

Follow the on-screen prompts.

#### 3. Install Dependencies

Run the following commands to install EdkRepo's dependencies:

`brew install bash-completion git git-gui pyenv`

`pyenv install 3.8.8`

`pyenv global 3.8.8`

During installation, you may be prompted to enter your password.

#### 4. Configure Shell for Pyenv and Git

To enable usage of Pyenv installed Python interpreters and Git command completions, run the following command:

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/tianocore/edk2-edkrepo/main/edkrepo_installer/mac-scripts/setup_git_pyenv_mac.sh)"`

Restart your shell so the Pyenv changes can take effect:

`exec $SHELL`

### Install EdkRepo

Extract the archive:

`tar -xzvf edkrepo-<version>.tar.gz`

If you are installing from source, you will need to build the distribution tarball using the following commands first:

1. `pip install wheel` (If not done already)
1. `cd build-scripts`
2. `./build_linux_installer.py`

Install EdkRepo:

`./install.py`

Restart your shell so the new Pyenv shim for EdkRepo can take effect:

`exec $SHELL`

## Windows Instructions
### Pre-Requisites
- Git 2.13.x or later
- Python 3.5 or later

Git 2.27.0 is the version that has received the most validation, though any version of Git 2.13 or later works fine. If you want to install 2.27.0, here are some links:
- [Direct Link - Git for Windows 2.27.0 - 64 Bit](https://github.com/git-for-windows/git/releases/download/v2.27.0.windows.1/Git-2.27.0-64-bit.exe)
- [Direct Link - Git for Windows 2.27.0 - 32 Bit](https://github.com/git-for-windows/git/releases/download/v2.27.0.windows.1/Git-2.27.0-32-bit.exe)

Python 3.8.8 or later is recommended due to performance improvements and [CVE-2021-3177](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-3177). You can get Python from here: https://www.python.org/

### Install Process
1. Run the installer .exe
2. Click Install

### Install From Source
To install from source, one must build and run the installer .exe using the instructions below at least once in order to setup the EdkRepo configuration files. One this is done, one may use the standard distutils method to install EdkRepo from source:

`py -3 setup.py install`

### Build Process
#### Build Pre-Requisites
- Visual Studio 2015 or later with the C# language and C++ compiler installed
- Python Wheel

Install Python wheel using the following:

`py -3 -m pip install wheel`

Open a command prompt and type the following:
1. `cd build-scripts`
2. `build_windows_installer.bat`

# Timeline
| Time | Event |
|:----:|:-----:|
| WW 10 2021 | Moved from edk2-staging to a dedicated repository |
| WW 26 2019 | Initial commit of EdkRepo |
|...|...|

# Maintainers
- Ashley DeSimone <ashley.e.desimone@intel.com>
- Nate DeSimone <nathaniel.l.desimone@intel.com>

# Known Issues
Please see https://github.com/tianocore/edk2-edkrepo/issues

# Related Links
- https://github.com/tianocore/edk2-edkrepo-manifest
- https://github.com/tianocore/edk2-platforms
