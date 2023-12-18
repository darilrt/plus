from .actions import init_project, build_project, run_project

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

    # build subparser
    build_parser = subparsers.add_parser('build', help='build the current project or the project specified')
    build_parser.add_argument('build_name', help='project name', default='.', nargs='?')
    build_parser.add_argument('-r', '--release', action='store_true', help='build in release mode')

    # run subparser
    run_parser = subparsers.add_parser('run', help='run the current project or the project specified')
    run_parser.add_argument('run_name', help='project name', default='.', nargs='?')
    run_parser.add_argument('-r', '--release', action='store_true', help='run in release mode')
    
    args = parser.parse_args()

    if hasattr(args, 'init_name'):
        init_project(args)
    
    elif hasattr(args, 'build_name'):
        build_project(args)
    
    elif hasattr(args, 'run_name'):
        run_project(args)

if __name__ == "__main__":
    main()