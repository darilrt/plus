import shutil
from plus.dependence import Dependence
from plus.config import Config
from typing import List

import subprocess
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
    
    def link(self, objs: List[str], dest: str, release=False) -> CompilationResult:
        libdirs = [f'-L{l}' for l in self.libdirs]
        libs = [f'-l{l}' for l in self.libs]

        result = subprocess.run([self.cxx, '-o', dest, *objs, *libs, *libdirs, *self.cxxflags])

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, dest)

        return CompilationResult(True, 0, '', '', dest)

    def copy_binaries(self, bindir: str):
        for binary in self.binaries:
            shutil.copy(binary, bindir)

    @staticmethod
    def from_config(config: Config) -> 'SourceCompiler':
        if not 'compiler' in config or config['compiler'] == '':
            print("No compiler set, defaulting to g++")
            config['compiler'] = 'g++'
            config.save()

        if not 'standard' in config or config['standard'] == '':
            print("No standard set, defaulting to c++17")
            config['standard'] = 'c++17'
            config.save()
        
        includes = config.get('includes', [])
        libdirs = config.get('libdirs', [])
        libs = config.get('libs', [])
        binaries = config.get('binaries', [])
        defines = config.get('defines', [])

        if 'requires' in config:
            deps = config.get('dependencies', {})
            for req in config['requires']:
                if req in deps:
                    dependence = Dependence(req, deps[req], '.')
                    includes += dependence.includes
                    libdirs += dependence.libdirs
                    libs += dependence.libs
                    binaries += dependence.binaries
                    defines += dependence.defines
        
        return SourceCompiler(
            cxx=config['compiler'],
            cxxflags=['-std=' + config['standard'], '-Wall', '-Wextra', '-pedantic'],
            includes=includes,
            libdirs=libdirs,
            libs=libs,
            binaries=binaries,
            defines=defines
        )