from plus.deps_repo import DepRepository
from plus.subprojects import Subprojects
from .config import Config
from .source_compiler import SourceCompiler
from .lockfile import LockFile
from .dependence import Dependence

import os

def exit(message: str=None):
    if message:
        print(message)
    os._exit(1)

class Project:
    folders = [
        'include',
        'src',
    ]

    def __init__(self, path: str, type="console-app"):
        self.path = path
        self.fullpath = os.path.abspath(path)
        self.name = os.path.basename(path)
        self.config = Config(self.fullpath + '/project.toml', type=type)
        self.lock = LockFile(self.fullpath + '/project.lock')

        if not self.config.is_valid:
            exit('project.toml is not valid')
    
    def validate(self):
        if not os.path.exists(self.path):
            exit(self.path + ' does not exist')
    
        if not os.path.exists(os.path.join(self.path, 'project.toml')):
            exit('project.toml does not exist')
        
        if not self.config.is_valid:
            exit('project.toml is not valid')
        
        if 'name' not in self.config["project"]:
            exit('Project name not found')

        self.lock.load()

        if not self.lock.is_valid:
            exit('project.lock is not valid')

    def create(self, ignore_exists=True):
        if os.path.exists(self.path):
            if os.listdir(self.path) != []:
                exit('Directory is not empty')
        else:
            os.mkdir(self.path)

        for folder in self.folders:
            os.mkdir(os.path.join(self.path, folder))
        
        with open(os.path.join(self.path, '.gitignore'), 'w') as f:
            f.write(GITIGNORE)
        
        if self.config["compiler"]['type'] == 'console-app' or self.config['type'] == 'app':
            with open(os.path.join(self.path, 'src', 'main.cpp'), 'w') as f:
                f.write(MAIN_APP)
        elif self.config["compiler"]['type'] == 'static-lib':
            with open(os.path.join(self.path, 'src', 'lib.cpp'), 'w') as f:
                f.write(MAIN_LIB)
            with open(os.path.join(self.path, 'include', 'lib.h'), 'w') as f:
                f.write(MAIN_LIB_H)
        elif self.config["compiler"]['type'] == 'shared-lib':
            with open(os.path.join(self.path, 'src', 'lib.cpp'), 'w') as f:
                f.write(MAIN_SHARED_LIB)
            with open(os.path.join(self.path, 'include', 'lib.h'), 'w') as f:
                f.write(MAIN_SHARED_LIB_H)
        
        self.config['project']['name'] = self.name
        self.config.save()

    def build(self, release=False):
        if not 'project' in self.config:
            exit('[project] section not found')

        if 'name' not in self.config["project"]:
            exit('Project name not found')

        subprojects = Subprojects(self.config, self.lock, self.path)
        subprojects.build()

        oldcwd = os.getcwd()
        os.chdir(self.path)

        compiler = SourceCompiler.from_config(self.config)

        objects = []

        def compile_dir(path: str, dest: str, release=False):
            for file in os.listdir(path):
                if os.path.isdir(os.path.join(path, file)):
                    compile_dir(
                        os.path.join(path, file), 
                        os.path.join(dest, file), 
                        release=release
                    )
                
                elif file.endswith('.cpp'):
                    file_path = os.path.join(path, file).replace('\\', '/')
                    stamp = os.path.getmtime(file_path)

                    if file_path in self.lock.files:
                        if self.lock.files[file_path]['stamp'] == stamp:
                            if 'object' in self.lock.files[file_path]:
                                objects.append(self.lock.files[file_path]['object'].replace('\\', '/'))
                                continue

                    result = compiler.compile(file_path, dest, release=release)

                    if not result.success:
                        print('\033[31m\u2717\033[0m', os.path.join(path, file))
                        exit()

                    objects.append(result.output)
                    self.lock.add_file(file_path, object=result.output.replace('\\', '/'))
                    
                    print('\033[32m\u2713\033[0m', os.path.join(path, file))
        
        if not os.path.exists('obj'):
            os.mkdir('obj')

        compile_dir('src', 'obj', release=release)

        if not 'type' in self.config['compiler']:
            exit('Compilation type not found')

        if self.config['compiler']['type'] == 'console-app' or self.config['compiler']['type'] == 'app':
            bindir = 'bin'
            dest = os.path.join(bindir, self.config['project']['name'])

            result = compiler.link(
                objects,
                dest,
                release=release,
                mwindows=self.config['compiler']['type'] == 'app'
            )
        else:
            bindir = 'lib'
            dest = os.path.join(bindir, self.config['project']['name'])

            result = compiler.link_lib(
                objects,
                dest,
                release=release,
                shared=self.config['compiler']['type'] == 'shared-lib'
            )

        compiler.copy_binaries(bindir)

        if not result.success:
            exit()
        
        print('\033[32m\u2713\033[0m compiled', self.config['project']['name'])
        
        self.lock.save()
        
        os.chdir(oldcwd)

    def run(self, release=False):
        if not 'compiler' in self.config:
            exit('[compiler] section not found')
        
        if 'project' not in self.config:
            exit('[project] section not found')
        
        if 'name' not in self.config['project']:
            exit('Project name not found')
        
        if 'type' not in self.config['compiler']:
            exit('Compilation type not found')

        if self.config['compiler']['type'] == 'console-app' or self.config['compiler']['type'] == 'app':
            self.build(release=release)
            print("Running", self.config['project']['name'] + "...")
            os.system(os.path.join(self.path, 'bin', self.config['project']['name']))
        else:
            print("Project is not an app, cannot run")

    def install_requirements(self):
        if 'requires' not in self.config:
            return
        
        if 'deps' not in self.config:
            self.config['deps'] = {}

        dep_repo = DepRepository()

        for requirement in self.config['requires']:
            print('Installing', requirement)

            if requirement in self.config['deps']:
                dependence = Dependence(
                    requirement,
                    self.config['deps'][requirement],
                    self.path
                )
                dependence.resolve()
            
            elif requirement in dep_repo:
                self.config['deps'][requirement] = dep_repo[requirement]
                self.config.save()
                
                dependence = Dependence(
                    requirement,
                    self.config['deps'][requirement],
                    self.path
                )
                dependence.resolve()

    def new_source(self, name: str, overwrite=False):
        if os.path.exists(os.path.join(self.path, 'src', name + '.cpp')):
            if not overwrite:
                exit(f'File {name}.cpp already exists')
        
        path: str = os.path.join(self.path, 'src', name + '.cpp')
        basedir: str = os.path.dirname(path)

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        with open(path, 'w+') as f:
            f.write('')
        
        print('\033[32m\u2713\033[0m created', os.path.join('src', name + '.cpp'))

    def new_header(self, name: str, overwrite=False):
        if os.path.exists(os.path.join(self.path, 'include', name + '.h')):
            if not overwrite:
                exit(f'File {name}.h already exists')

        path: str = os.path.join(self.path, 'include', name + '.h')
        basedir: str = os.path.dirname(path)

        if not os.path.exists(basedir):
            os.makedirs(basedir)
        
        with open(path, 'w+') as f:
            f.write('#pragma once\n')
        
        print('\033[32m\u2713\033[0m created', os.path.join('include', name + '.h'))

    def add_dep(self, name: str):
        if 'requires' not in self.config:
            self.config['requires'] = {}

        if name in self.config['requires']:
            exit('Requirement already exists')

        dep_repo = DepRepository()
        dep_repo.upgrade()

        if name not in dep_repo and name not in self.config.get('deps', {}):
            exit('Dependence not found')
        
        if name in dep_repo:
            if 'deps' not in self.config:
                self.config['deps'] = {}

            self.config['deps'][name] = dep_repo[name]
        
        self.config['requires'][name] = '*'
        self.config.save()

        dep = Dependence(name, self.config['deps'][name], self.path)
        dep.resolve()

GITIGNORE = '''\
# Compiled Object files
*.slo
*.lo
*.o
*.obj

# Precompiled Headers
*.gch
*.pch

# Compiled Dynamic libraries
*.so
*.dylib
*.dll

# Fortran module files
*.mod
*.smod

# Compiled Static libraries
*.lai
*.la
*.a
*.lib

# Executables
*.exe
*.out

# Vendor
vendor/
'''

MAIN_APP = '''\
#include <iostream>

int main() {
    std::cout << "Hello, world!" << std::endl;
    return 0;
}
'''

MAIN_LIB = '''\
#include <iostream>

#include "lib.h"

void hello() {
    std::cout << "Hello, world!" << std::endl;
}
'''

MAIN_LIB_H = '''\
#pragma once

void hello();
'''

MAIN_SHARED_LIB = '''\
#include <iostream>

#include "lib.h"

void hello() {
    std::cout << "Hello, world!" << std::endl;
}
'''

MAIN_SHARED_LIB_H = '''\
#pragma once

#if defined(_MSC_VER)
#   if defined(SHARED_LIB)
#       define API __declspec(dllexport)
#   else
#       define API __declspec(dllimport)
#   endif
#elif defined(__GNUC__)
#   if defined(SHARED_LIB)
#       define API __attribute__((visibility("default")))
#   else
#       define API
#   endif
#else
#   define API
#endif

API void hello();
'''