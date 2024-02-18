[![PyPi Package Version](https://img.shields.io/pypi/v/plus-cpp)](https://pypi.org/project/plus-cpp/)

# <p align="center"><img src="https://raw.githubusercontent.com/darilrt/plus/master/assets/logo.png" width="25"/> Plus</p>

Plus is a simple command line tool to manage c++ projects.

## Features

- [x] Create a new project
- [x] Run the project
- [x] Build the project
- [x] Build static library
- [x] Build shared library
- [x] Build application without console
- [x] Build console application
- [x] Manage multiple subprojects
- [x] Manage dependencies
- [x] Custom dependencies
- [x] Add a new source file
- [x] Add a new header file
- [x] Custom build commands for dependencies

## Requirements

- python3
- git
- gcc

## Installation

### Pip

Installation using pip (a Python package manager):

```bash
$ pip install plus-cpp
```

### From source

```bash
$ git clone
$ cd plus
$ python3 setup.py install
```

## Usage

```bash
$ plus --help
```

## Hello World

```bash
$ plus init hello_world
$ cd hello_world
$ plus run
```

## Subprojects

First create a new project to be the parent project.

```bash
$ plus init parent_project
```

Then create a new project to be the child project.

```bash
$ cd parent_project
$ plus init child_project --lib
```

Now you can add the child project to the parent project.
In the parent project directory, open the `project.toml` file and add the child project to the `subprojects` list.

```toml
...
[subprojects]
child_project = { path = "child_project" }
...
```

Now you can build the parent project and the child project will be built too.

```bash
$ plus build
```
