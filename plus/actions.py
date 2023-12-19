from .project import Project
from .deps_repo import DepRepository
import os

def init_project(args):
    type = 'console-app'

    if args.app:
        type = 'app'
    elif args.lib:
        type = 'static-lib'
    elif args.shared_lib:
        type = 'shared-lib'

    if os.path.exists(args.init_name):
        exit('Project already exists')
    
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

def install_project(args):
    project = Project('.')
    project.validate()
    project.install_requirements()

def new_project(args):
    project = Project('.')
    project.validate()

    if args.source:
        project.new_source(args.new_name, overwrite=args.overwrite)
    elif args.header:
        project.new_header(args.new_name, overwrite=args.overwrite)
    else:
        project.new_source(args.new_name, overwrite=args.overwrite)
        project.new_header(args.new_name, overwrite=args.overwrite)
    
def upgrade_project(args):
    dep = DepRepository()
    dep.upgrade()

def add_project(args):
    project = Project('.')
    project.validate()
    project.add_dep(args.add_name)