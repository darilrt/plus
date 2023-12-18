from .project import Project
import os

def init_project(args):
    path: os.PathLike = os.path.join(os.getcwd(), args.init_name)

    type = 'console-app'

    if args.app:
        type = 'app'
    elif args.lib:
        type = 'static-lib'
    elif args.shared_lib:
        type = 'shared-lib'
    
    project = Project(path, type=type)
    project.create()

def build_project(args):
    path: os.PathLike = os.path.join(os.getcwd(), args.build_name)

    project = Project(path)
    project.build(release=args.release)

def run_project(args):
    path: os.PathLike = os.path.join(os.getcwd(), args.run_name)

    project = Project(path)
    project.run(release=args.release)