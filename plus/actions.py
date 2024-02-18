from plus.compiler import Compiler
from plus.project import Project
from plus.repository import Repository

from rich import print
import rich
import os
import re

def init_project(args):
    is_lib: bool = args.lib
    is_shared_lib: bool = args.shared_lib

    type: str = 'console-app'
    if is_lib:
        type = 'static-lib'
    elif is_shared_lib:
        type = 'shared-lib'
    
    exp: str = r'^[a-zA-Z0-9_]+$'

    if not re.match(exp, args.name):
        print(f"Invalid project name [bold red]{args.name} [/bold red]")
        return

    project = Project.create(args.name, type)

def build_project(args):
    print(f"Building project [bold blue]{args.path}[/bold blue]")
    project = Project.open(args.path)
    compiler = Compiler.from_project(project)
    compiler.compile()

def run_project(args):
    print(f"Building project [bold blue]{args.path}[/bold blue]")
    project = Project.open(args.path)
    compiler = Compiler.from_project(project)
    exec: str = compiler.compile()

    if exec:
        print(f"Running [bold green]{exec}[/bold green]")
        os.system(exec)

def install_project(args):
    print(f"Installing dependencies")
    project = Project.open('.')

    if 'requires' not in project.config:
        print(f"No dependencies found")
        return
    
    project.install_deps()
    
    for sub in project.get_subprojects():
        sub.install_deps()

def new_project(args):
    print(f"Creating new file [bold blue]{args.new_name}[/bold blue]")

def upgrade_project(args):
    Repository.upgrade()

def add_project(args):
    project = Project.open('.')

    if 'requires' not in project.config:
        project.config['requires'] = []

    if args.name in project.config['requires']:
        print(f"Dependency [bold green]{args.name}[/bold green] already exists")
        return

    if 'deps' not in project.config and args.name in project.config['deps']:
        project.config['requires'].append(args.name)
    else:
        Repository.load()

        if Repository.has(args.name):
            project.config['requires'].append(args.name)

        else:
            print(f"Dependency [bold red]{args.name}[/bold red] not found")
            return

    rich.print(f"Added dependency [bold green]{args.name}[/bold green]")
    
    project.save_config()

def clean_project(args):
    project = Project.open('.')
    project.clean(
        deps=args.deps,
        files=args.files,
        subprojects=args.subprojects
    )