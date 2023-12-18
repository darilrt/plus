from .config import Config
from .source_compiler import SourceCompiler
from .lockfile import LockFile
from .dependence import Dependence

import os
import json

def exit(message: str=None):
    if message:
        print(message)
    os._exit(1)

class Project:
    folders = [
        'bin',
        'obj',
        'include',
        'src',
    ]

    def __init__(self, path: str, type="console-app"):
        self.path = path
        self.name = os.path.basename(path)
        self.config = Config(path + '/project.json', type=type)
        self.lock = LockFile(path + '/project.lock')

        if not self.config.is_valid:
            exit('project.json is not valid')
    
    def validate(self):
        if not os.path.exists(self.path):
            exit(self.path + ' does not exist')
    
        if not os.path.exists(os.path.join(self.path, 'project.json')):
            exit('project.json does not exist')
        
        if not self.config.is_valid:
            exit('project.json is not valid')
        
        if 'name' not in self.config:
            exit('Project name not found')

        self.lock.load()

        if not self.lock.is_valid:
            exit('project.lock is not valid')

    def create(self, ignore_exists=True):
        if os.path.exists(self.path):
            if not ignore_exists:
                exit('Project already exists')
        else:
            os.mkdir(self.path)

        for folder in self.folders:
            os.mkdir(os.path.join(self.path, folder))
        
        with open(os.path.join(self.path, '.gitignore'), 'w') as f:
            f.write(GITIGNORE)
        
        if self.config['type'] == 'console-app' or self.config['type'] == 'app':
            with open(os.path.join(self.path, 'src', 'main.cpp'), 'w') as f:
                f.write(MAIN_APP)        
        elif self.config['type'] == 'static-lib':
            with open(os.path.join(self.path, 'src', 'lib.cpp'), 'w') as f:
                f.write(MAIN_LIB)
            with open(os.path.join(self.path, 'include', 'lib.h'), 'w') as f:
                f.write(MAIN_LIB_H)
        elif self.config['type'] == 'shared-lib':
            with open(os.path.join(self.path, 'src', 'lib.cpp'), 'w') as f:
                f.write(MAIN_SHARED_LIB)
            with open(os.path.join(self.path, 'include', 'lib.h'), 'w') as f:
                f.write(MAIN_SHARED_LIB_H)
        
        self.config['name'] = self.name
        self.config.save()

    def build(self, release=False):
        if 'name' not in self.config:
            exit('Project name not found')

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
                    file_path = os.path.join(path, file)
                    stamp = os.path.getmtime(file_path)

                    if file_path in self.lock.files:
                        if self.lock.files[file_path]['stamp'] == stamp:
                            if 'object' in self.lock.files[file_path]:
                                objects.append(self.lock.files[file_path]['object'])
                                continue

                    result = compiler.compile(file_path, dest, release=release)

                    if not result.success:
                        exit(result.returncode)

                    objects.append(result.output)
                    self.lock.add_file(file_path, object=result.output)
                    
                    print('\033[32m\u2713\033[0m', os.path.join(path, file))
        
        compile_dir(os.path.join(self.path, 'src'), os.path.join(self.path, 'obj'), release=release)

        if self.config['type'] == 'console-app' or self.config['type'] == 'app':
            result = compiler.link(
                objects, 
                os.path.join(self.path, 'bin', self.config['name']), 
                release=release
            )

            if not result.success:
                exit(result.returncode)
            
            print('\033[32m\u2713\033[0m compiled', self.config['name'])
            
            self.lock.save()

    def run(self, release=False):
        if self.config['type'] == 'console-app' or self.config['type'] == 'app':
            self.build(release=release)
            print("Running", self.config['name'] + "...")
            os.system(os.path.join(self.path, 'bin', self.config['name']))
        else:
            print("Project is not an app, cannot run")

    def install_requirements(self):
        if 'requires' not in self.config:
            return

        for requirement in self.config['requires']:
            print('Installing', requirement)

            if requirement in self.config['dependencies']:
                dependence = Dependence(
                    requirement,
                    self.config['dependencies'][requirement],
                    self.path
                )
                dependence.resolve()


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