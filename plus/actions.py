from .project import Project
import os

def init_project(args):
    type = 'console-app'

    if args.app:
        type = 'app'
    elif args.lib:
        type = 'static-lib'
    elif args.shared_lib:
        type = 'shared-lib'
    
    project = Project(args.init_name, type=type)
    project.create()

def build_project(args):
    project = Project(args.build_name)
    project.validate()
    project.build(release=args.release)

def run_project(args):
    project = Project(args.run_name)
    project.validate()
    project.run(release=args.release)