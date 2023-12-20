from .actions import init_project
from .actions import build_project
from .actions import run_project
from .actions import install_project
from .actions import new_project
from .actions import upgrade_project
from .actions import add_project

import argparse

def main():
    parser = argparse.ArgumentParser(
        prog='plus',
        description='plus is a library for managing c++ projects',
        epilog='')

    # help argument
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.4.1')

    # subparsers
    subparsers = parser.add_subparsers()

    # init subparser
    init_parser = subparsers.add_parser('init', help='create a new c++ project')
    init_parser.add_argument('init_name', help='project name')
    init_parser.add_argument('-l', '--lib', action='store_true', help='create a library project')
    init_parser.add_argument('-s', '--shared-lib', action='store_true', help='create a shared library project')
    init_parser.add_argument('-a', '--app', action='store_true', help='create an application project with no console')
    init_parser.set_defaults(func=init_project)

    # build subparser
    build_parser = subparsers.add_parser('build', help='build the current project or the project specified')
    build_parser.add_argument('build_name', help='project name', default='.', nargs='?')
    build_parser.add_argument('-r', '--release', action='store_true', help='build in release mode')
    build_parser.set_defaults(func=build_project)

    # run subparser
    run_parser = subparsers.add_parser('run', help='run the current project or the project specified')
    run_parser.add_argument('run_name', help='project name', default='.', nargs='?')
    run_parser.add_argument('-r', '--release', action='store_true', help='run in release mode')
    run_parser.set_defaults(func=run_project)

    # install subparser
    install_parser = subparsers.add_parser('install', help='install all dependencies of the current project')
    install_parser.set_defaults(func=install_project)

    # new subparser
    new_parser = subparsers.add_parser('new', help='create a new c++ file in the current project, by default creates a header and source file')
    new_parser.add_argument('new_name', help='file path and name (without extension) to create (e.g. test/main)')
    new_parser.add_argument('-H', '--header', action='store_true', help='create header file')
    new_parser.add_argument('-s', '--source', action='store_true', help='create source file')
    new_parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite existing file')
    new_parser.set_defaults(func=new_project)

    # upgrade subparser
    upgrade_parser = subparsers.add_parser('upgrade', help='upgrade the plus repository')
    upgrade_parser.set_defaults(func=upgrade_project)

    # add subparsers
    add_parser = subparsers.add_parser('add', help='add a dependency to the current project')
    add_parser.add_argument('add_name', help='dependency name')
    add_parser.set_defaults(func=add_project)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)

if __name__ == "__main__":
    main()