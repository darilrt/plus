from .config import Config
from .source import SourceCompiler

import os
import json

class Project:
    folders = [
        'bin',
        'obj',
        'include',
        'src',
    ]

    def __init__(self, path, type="console-app"):
        self.path = path
        self.name = os.path.basename(path)
        self.config = Config(path + '/project.json', type=type)

        if not self.config.is_valid:
            exit()
    
    def create(self, ignore_exists=True):
        if os.path.exists(self.path):
            if not ignore_exists:
                raise Exception('Project already exists')
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
        compiler = SourceCompiler.from_config(self.config)

        objects = []

        def compile_dir(path, dest, release=False):
            for file in os.listdir(path):
                if os.path.isdir(os.path.join(path, file)):
                    compile_dir(
                        os.path.join(path, file), 
                        os.path.join(dest, file), 
                        release=release
                    )
                
                elif file.endswith('.cpp'):
                    result = compiler.compile(os.path.join(path, file), dest, release=release)

                    if not result[0]:
                        exit(result[1])

                    objects.append(result[4])
                    
                    print('\033[32m\u2713\033[0m', os.path.join(path, file))
        
        compile_dir(os.path.join(self.path, 'src'), os.path.join(self.path, 'obj'), release=release)

        if self.config['type'] == 'console-app' or self.config['type'] == 'app':
            result = compiler.link(objects, os.path.join(self.path, 'bin', self.name), release=release)

            if not result[0]:
                exit(result[1])
            
            print('\033[32m\u2713\033[0m compiled', os.path.join(self.path, 'bin', self.name))

    def run(self, release=False):
        if self.config['type'] == 'console-app' or self.config['type'] == 'app':
            self.build(release=release)
            os.system(os.path.join(self.path, 'bin', self.name))
        else:
            print("Project is not an app, cannot run")

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