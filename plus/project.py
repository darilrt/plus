from plus.repository import Repository
from plus.dependency import Dependency
from plus.default_files import Defualt
from plus.compiler import Compiler, CompilerDeps

from rich.console import Console
import shutil
import rich
import toml
import os

class Project:
    def __init__(self, name: str, path: str) -> None:
        self.name: str = name
        self.path: str = os.path.abspath(path)
        self.config_path: str = os.path.join(self.path, "plus.toml")
        self.config: dict = {}
        self.lock: dict = {}
    
    def info(self, tabs: int = 0) -> None:
        console = Console()
        console.tab_size = 4 + tabs * 4

        console.print(f"\tProject: [bold yellow]{self.name}[/bold yellow]")
        console.print(f"\tPath: [bold green]{self.path}[/bold green]")
        console.print(f"\tRequires: [bold blue]{', '.join(self.config['requires']) if 'requires' in self.config else '[]'}[/bold blue]")

    def install_deps(self) -> None:
        if 'requires' not in self.config:
            return

        if 'vendor' not in os.listdir(self.path):
            os.makedirs(os.path.join(self.path, 'vendor'))
        
        for requiement in self.config['requires']:
            dep: dict = None

            if 'deps' in self.config:
                if requiement in self.config['deps']:
                    dep = self.config['deps'][requiement]

            Repository.load()
            
            if dep is None and Repository.has(requiement):
                dep = Repository.get(requiement)

                if dep is None:
                    rich.print(f"Dependency [bold yellow]{requiement}[/bold yellow] not found in [bold green]{os.path.join(self.path, 'plus.toml')}[/bold green]")
                    exit(1)
            
            if dep is None:
                rich.print(f"Dependency [bold yellow]{requiement}[/bold yellow] not found")
                exit(1)

            dep: Dependency = Dependency.from_dict(dep, requiement)
            dep.install(os.path.join(self.path, 'vendor'))

    def get_subprojects(self) -> list["Project"]:
        if 'subprojects' not in self.config:
            return []
        
        subs: list["Project"] = []

        for sub in self.config['subprojects']:
            path: str = os.path.join(self.path, self.config['subprojects'][sub]['path'])

            if not os.path.exists(path):
                rich.print(f"Subproject [bold yellow]{sub}[/bold yellow] not found in [bold green]{os.path.join(self.path, 'plus.toml')}[/bold green]" )
                exit(1)

            subs.append(Project.open(path))
        
        return subs

    def get_compiler_deps(self) -> CompilerDeps:
        deps = CompilerDeps()

        if 'requires' in self.config:
            requires = self.config['requires']

            for requiement in requires:
                dep: dict = None

                if 'deps' in self.config:
                    if requiement in self.config['deps']:
                        dep = self.config['deps'][requiement]

                Repository.load()
                
                if dep is None and Repository.has(requiement):
                    dep = Repository.get(requiement)

                    if dep is None:
                        rich.print(f"Dependency [bold yellow]{requiement}[/bold yellow] not found in [bold green]{os.path.join(self.path, 'plus.toml')}[/bold green]")
                        exit(1)
                
                if dep is None:
                    rich.print(f"Dependency [bold yellow]{requiement}[/bold yellow] not found")
                    exit(1)

                dep: Dependency = Dependency.from_dict(dep, requiement)
                deps.merge(dep.get_compiler_deps(os.path.join(self.path, 'vendor')))

        if 'compiler' in self.config:
            cmop = self.config['compiler']

            if 'includes' in cmop:
                deps.include_dirs.extend([
                    os.path.join(self.path, inc) for inc in cmop['includes']
                ])

            if 'defines' in cmop:
                deps.defines.extend(cmop['defines'])
            
            if 'flags' in cmop:
                deps.flags.extend(cmop['flags'])

            if 'binaries' in cmop:
                deps.binaries.extend(cmop['binaries'])
            
        if 'linker' in self.config:
            cmop = self.config['linker']

            if 'libdirs' in cmop:
                deps.lib_dirs.extend(cmop['libdirs'])

            if 'libs' in cmop:
                deps.libs.extend(cmop['libs'])

            if 'flags' in cmop:
                deps.flags.extend(cmop['flags'])


        old_path: str = os.getcwd()
        os.chdir(self.path)
        for root, dirs, files in os.walk('src'):
            for file in files:
                if file.endswith('.cpp') or file.endswith('.c'):
                    deps.sources.append(os.path.join(self.path, root, file))

        os.chdir(old_path)

        return deps

    def new_source(self, name: str, overwrite: bool = False, default: str = "") -> None:
        if os.path.exists(f'src/{name}') and not overwrite:
            exit(f"Source file {name} already exists")
        
        basedir: str = os.path.dirname(f'src/{name}')

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        with open(f'src/{name}', 'w') as f:
            f.write(default)

    def new_header(self, name: str, overwrite: bool = False, default: str = "") -> None:
        if os.path.exists(f'include/{name}') and not overwrite:
            exit(f"Header file {name} already exists")
        
        basedir: str = os.path.dirname(f'include/{name}')

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        with open(f'include/{name}', 'w') as f:
            f.write(default)
        
    def save_config(self) -> None:
        path: str = os.path.join(self.path, 'plus.toml')
        with open(path, 'w') as f:
            f.write(toml.dumps(self.config))
    
    def save_lock(self) -> None:
        path: str = os.path.join(self.path, 'plus.lock')
        with open(path, 'w') as f:
            f.write(toml.dumps(self.lock))

    def clean(self, files=True, deps=True, subprojects=True) -> None:
        old_path: str = os.getcwd()
        os.chdir(self.path)
        
        if files:
            if os.path.exists('bin'):
                shutil.rmtree('bin')
            if os.path.exists('lib'):
                shutil.rmtree('lib')
            if os.path.exists('obj'):
                shutil.rmtree('obj')
            
            self.lock = {}

        if deps:
            if os.path.exists('vendor'):
                shutil.rmtree('vendor')

        os.chdir(old_path)

        if subprojects:
            for sub in self.get_subprojects():
                sub.clean(files, deps, subprojects)

        self.save_lock()

    @staticmethod
    def open(name: str) -> "Project":
        old_path: str = os.getcwd()
        os.chdir(name)

        if not os.path.exists('plus.toml'):
            rich.print(f"Project not found in {os.getcwd()}")
            exit(1)

        if not os.path.exists('plus.lock'):
            with open('plus.lock', 'w') as f:
                f.write(toml.dumps({}))
        
        lock: dict = {}
        with open('plus.lock', 'r') as f:
            lock = toml.load(f)
        
        config: dict = {}

        with open('plus.toml', 'r') as f:
            config = toml.load(f)

        if 'name' not in config:
            rich.print(f"Invalid project file")
            rich.print(f'Missing [bold red]name[/bold red] in [bold yellow]' + os.path.join(os.getcwd(), 'plus.toml') + '[/bold yellow] file')
            exit(1)

        project = Project(config['name'], os.getcwd())
        project.config = config
        project.lock = lock

        os.chdir(old_path)
        return project

    @staticmethod
    def create(name: str, type: str) -> "Project":
        project = Project(name, os.path.join(os.getcwd(), name))

        if not os.path.exists(name):
            os.mkdir(name)
        
        os.chdir(name)

        if not os.path.exists('include'):
            os.mkdir('include')
        
        if not os.path.exists('src'):
            os.mkdir('src')

        if type == 'console-app':
            project.new_source('main.cpp', default=Defualt.MAIN)
        elif type == 'app':
            project.new_source('main.cpp', default=Defualt.MAIN)
        elif type == 'static-lib':
            project.new_source('lib.cpp', default=Defualt.LIB_SOURCE)
            project.new_header('lib.hpp', default=Defualt.STATIC_LIB_HEADER)
        elif type == 'shared-lib':
            project.new_source('lib.cpp', default=Defualt.LIB_SOURCE)
            project.new_header('lib.hpp', default=Defualt.SHARED_LIB_HEADER)

        with open('.gitignore', 'w') as f:
            f.write(Defualt.GITIGNORE)
        
        with open('plus.toml', 'w') as f:
            f.write(toml.dumps(Defualt.CONFIG(name, type)))

        rich.print(f"Created project [bold yellow]{name}[/bold yellow]")

        return project