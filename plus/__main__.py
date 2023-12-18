from .actions import init_project, build_project, run_project, install_project

import argparse

def main():
    parser = argparse.ArgumentParser(
        prog='plus',
        description='plus is a library for managing c++ projects',
        epilog='')

    # help argument
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0')

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

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()