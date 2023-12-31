import platform
import shutil
import subprocess
import os
import glob

from plus.config import Config
from plus.default_files import Defualt
from plus.rtext import *
from plus.source_compiler import CompilationResult, SourceCompiler

class Project:
    def __init__(self: "Project", path: str, config: Config, type="console-app") -> None:
        self.path = path
        self.fullpath = os.path.abspath(path).replace("\\", "/")
        self.config = config
    
    def compile(self: "Project", debug=False, compiler: SourceCompiler=None, force=False, optional_compile=False, root_config=None) -> None:
        if not os.path.exists(self.fullpath):
            os.makedirs(self.fullpath)

        subprojects = self.config.get_subprojects(path=self.fullpath)
        subprojects.compile(debug=debug)

        root_config = self.config if not root_config else root_config

        rm = self.config.get_requirement_manager(ignore_deps=[self.config.name], root_config=root_config)
        if debug and len(rm.requirements) > 0:
            print(f"Building dependencies for {rtext(self.config.name, color=color.green, style=style.bold)}")
            rm.list()
        
        for req in rm:
            req.compile()

        if not compiler:
            compiler = SourceCompiler.from_config(self.config.dict)

        sp = subprojects.get_compiler_config()

        compiler.includes += list(dict.fromkeys(rm.includes + sp["includes"]))
        compiler.libs += list(reversed(dict.fromkeys(rm.libs + sp["libs"])))
        compiler.libdirs += list(dict.fromkeys(rm.libdirs + sp["libdirs"]))
        compiler.binaries += list(dict.fromkeys(rm.binaries + sp["binaries"]))
        compiler.defines += list(dict.fromkeys(rm.defines + sp["defines"]))

        self._script('pre-build')

        if not optional_compile:
            self._compile(compiler)
        elif 'linker' in self.config.dict and 'type' in self.config.dict['linker']:
            self._compile(compiler)
            print(f"Compiled {rtext(self.config.name, color=color.green, style=style.bold)} " + rtext("✓", color=color.green, style=style.bold))
        
        self._script('post-build')

    def run(self: "Project") -> None:
        binary = f'bin/{self.config.name}'

        self.compile(debug=True)

        print(f"Running {rtext(self.config.name, color=color.green, style=style.bold)}")
        subprocess.run([binary])

    def new_source(self: "Project", name: str, overwrite=False, default="") -> None:
        if os.path.exists(f'src/{name}') and not overwrite:
            exit(f"Source file {name} already exists")
        
        with open(f'src/{name}', 'w') as f:
            f.write(default)

    def new_header(self: "Project", name: str, overwrite=False, default="") -> None:
        if os.path.exists(f'include/{name}') and not overwrite:
            exit(f"Header file {name} already exists")
        
        with open(f'include/{name}', 'w') as f:
            f.write(default)
            
    def clean(self, files=True, deps=True, subprojects=True) -> None:
        lockfile = self.config.lockfile
        
        if files:
            if os.path.exists('bin'):
                shutil.rmtree('bin')
            if os.path.exists('lib'):
                shutil.rmtree('lib')
            if os.path.exists('obj'):
                shutil.rmtree('obj')
            
            lockfile.files = {}

        if deps:
            if os.path.exists('vendor'):
                shutil.rmtree('vendor')
            lockfile.deps = {}

        if subprojects:
            self.config.get_subprojects(path=self.fullpath).clean(files=files, deps=deps)

        lockfile.save()


    @staticmethod
    def create(config: Config) -> "Project":
        type = config.type
        project = Project('.', config)

        os.mkdir('include')
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

        return project

    def _compile(self: "Project", compiler: SourceCompiler) -> None:
        src_files = glob.glob(f'{self.fullpath}/src/**/*.cpp', recursive=True)
    	
        objects = []

        if not os.path.exists(f'{self.fullpath}/obj'):
            os.mkdir(f'{self.fullpath}/obj')

        files = self.config.lockfile.get_files()

        is_first = True
        for src_file in src_files:
            src = src_file.replace("\\", "/")
            dest = os.path.dirname(src_file.replace("\\", "/").replace(f'{self.fullpath}/src', f'{self.fullpath}/obj'))

            if src in files:
                if os.path.getmtime(src) == files[src]['stamp']:
                    objects.append(files[src]['object'])
                    continue
            
            result: CompilationResult = compiler.compile(src=src, dest=dest)

            if not result.success:
                print(result.stderr)
                exit(f"Could not compile {src}")

            if not is_first:
                print('\033[F\033[K', end='')
            else:
                is_first = False
            print(f"Compiled {rtext(src, color=color.green, style=style.bold)} " + rtext("✓", color=color.green, style=style.bold))
            
            objects.append(result.output)
            files[src] = {
                'stamp': os.path.getmtime(src),
                'object': result.output.replace("\\", "/")
            }

        result = None

        if len(objects) > 0 and 'linker' in self.config.dict and 'type' in self.config.dict['linker']:
            if self.config.dict['linker']['type'] == 'static-lib':
                result = compiler.link_lib(objs=objects, dest=f'{self.fullpath}/lib/lib{self.config.name}')
                compiler.copy_binaries(bindir=f'{self.fullpath}/lib')
            elif self.config.dict['linker']['type'] == 'shared-lib':
                result = compiler.link_lib(objs=objects, dest=f'{self.fullpath}/lib/lib{self.config.name}', shared=True)
                compiler.copy_binaries(bindir=f'{self.fullpath}/lib')
            elif self.config.dict['linker']['type'] == 'console-app':
                result = compiler.link(objs=objects, dest=f'{self.fullpath}/bin/{self.config.name}')
                compiler.copy_binaries(bindir=f'{self.fullpath}/bin')
            elif self.config.dict['linker']['type'] == 'app':
                result = compiler.link(objs=objects, dest=f'{self.fullpath}/bin/{self.config.name}', mwindows=True)
                compiler.copy_binaries(bindir=f'{self.fullpath}/bin')

            if not result.success:
                print(result.stderr)
                exit(f"Could not link {self.config.name}")

        self.config.lockfile.save()

    def _script(self: "Project", name: str, config: dict=None) -> None:
        script = f'{name}'
        current_platform = platform.system().lower()
        cmds = []

        if not config:
            config = self.config.dict
        
        if script in config:
            cmds = config[script]
        
        if current_platform in config and script in config[current_platform]:
            cmds = config[current_platform][script]

        old_dir = os.getcwd()
        os.chdir(self.fullpath)

        for cmd in cmds:
            try:
                result = subprocess.run(cmd, shell=True, check=True)
                if result.returncode != 0:
                    exit(f"Build script failed with exit code {result.returncode}")
            except subprocess.CalledProcessError as e:
                exit(e)
        
        os.chdir(old_dir)