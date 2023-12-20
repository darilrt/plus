from plus.deps_repo import DepRepository
from plus.dependence import Dependence
from plus.config import Config
from typing import List

import subprocess
import platform
import shutil
import os

class CompilationResult:
    def __init__(self, success: bool, returncode: int, stderr: str, stdout: str, output: str):
        self.success = success
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout
        self.output = output

class SourceCompiler:
    def __init__(self, cxx='', cxxflags=[], libdirs=[], includes=[], libs=[], binaries=[], defines=[]):
        self.ar = 'ar'
        self.cxx = cxx
        self.cxxflags = cxxflags
        self.libdirs = libdirs
        self.includes = includes
        self.libs = libs
        self.binaries = binaries
        self.defines = defines

    def compile(self, src: str, dest: str, release=False) -> CompilationResult:
        if not os.path.exists(dest):
            os.mkdir(dest)
        
        obj = os.path.join(dest, os.path.splitext(os.path.basename(src))[0] + '.o')

        includes = [f'-I{i}' for i in self.includes]
        defines = [f'-D{d}' for d in self.defines]

        result = subprocess.run([self.cxx, '-c', src, '-o', obj, *includes, *defines, *self.cxxflags])

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, obj)
        
        return CompilationResult(True, 0, '', '', obj)
    
    def link(self, objs: List[str], dest: str, release=False, mwindows=False) -> CompilationResult:
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        
        libdirs = [f'-L{l}' for l in self.libdirs]
        libs = [f'-l{l}' for l in self.libs]

        if mwindows:
            libs.append('-mwindows')

        cmd = [
            self.cxx,
            '-o', dest,
            *objs,
            *libdirs,
            *libs,
            *self.cxxflags
        ]

        print(" ".join(cmd))
        result = subprocess.run(cmd)

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, dest)

        return CompilationResult(True, 0, '', '', dest)

    def link_lib(self, objs: List[str], dest: str, release=False, shared=False) -> CompilationResult:
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        
        libdirs = [f'-L{l}' for l in self.libdirs]
        libs = [f'-l{l}' for l in self.libs]

        ext = '.a' if not shared else '.so'

        if platform.system().lower() == 'windows':
            ext = '.lib' if not shared else '.dll'
        elif platform.system().lower() == 'darwin':
            ext = '.a' if not shared else '.dylib'

        if shared:
            result = subprocess.run([
                self.cxx,
                '-shared',
                '-o', dest + ext,
                *objs,
                *libs,
                *libdirs,
                *self.cxxflags
            ])
            
        else:
            result = subprocess.run([
                self.ar,
                'rcs',
                dest + ext,
                *objs
            ])

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, dest)

        return CompilationResult(True, 0, '', '', dest)


    def copy_binaries(self, bindir: str):
        if not os.path.exists(bindir):
            os.mkdir(bindir)
        
        for binary in self.binaries:
            if not os.path.exists(binary):
                print(f'Binary {binary} does not exist')
                continue

            shutil.copy(binary, bindir)

    @staticmethod
    def from_config(config: Config) -> 'SourceCompiler':
        if not 'compiler' in config:
            config['compiler'] = {}

        if not 'cxx' in config['compiler'] or config['compiler']['cxx'] == '':
            print("No compiler set, defaulting to g++")
            config['compiler']['cxx'] = 'g++'
            config.save()

        if not 'standard' in config['compiler'] or config['compiler']['standard'] == '':
            print("No standard set, defaulting to c++17")
            config['compiler']['standard'] = 'c++17'
            config.save()
        
        includes = config['compiler'].get('includes', [])
        libdirs = config['compiler'].get('libdirs', [])
        libs = config['compiler'].get('libs', [])
        binaries = config['compiler'].get('binaries', [])
        defines = config['compiler'].get('defines', [])

        dep_repo = DepRepository()

        if 'requires' in config:
            deps = config.get('deps', {})
            for req in config['requires']:
                if req in deps:
                    dependence = Dependence(req, deps[req], '.')
                    includes += dependence.includes
                    libdirs += dependence.libdirs
                    libs += dependence.libs
                    binaries += dependence.binaries
                    defines += dependence.defines
                
                elif req in dep_repo:
                    dependence = Dependence(req, dep_repo[req], '.')
                    includes += dependence.includes
                    libdirs += dependence.libdirs
                    libs += dependence.libs
                    binaries += dependence.binaries
                    defines += dependence.defines
        
        return SourceCompiler(
            cxx=config['compiler']['cxx'],
            cxxflags=['-std=' + config['compiler']['standard'], '-Wall', '-Wextra', '-pedantic'],
            includes=includes,
            libdirs=libdirs,
            libs=libs,
            binaries=binaries,
            defines=defines
        )