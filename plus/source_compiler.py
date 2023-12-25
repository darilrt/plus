from plus.repository import Repository
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
    def __init__(self, cxx='', cxxflags=[], libdirs=[], includes=[], libs=[], binaries=[], defines=[], warnings=[]):
        self.ar = 'ar'
        self.cxx = cxx
        self.cxxflags = cxxflags
        self.libdirs = libdirs.copy()
        self.includes = includes.copy()
        self.libs = libs.copy()
        self.binaries = binaries.copy()
        self.defines = defines.copy()
        self.warnings = warnings

    def compile(self, src: str, dest: str, release=False) -> CompilationResult:
        if not os.path.exists(dest):
            os.mkdir(dest)
        
        obj = os.path.join(dest, os.path.splitext(os.path.basename(src))[0] + '.o')

        includes = [f'-I{i}' for i in self.includes]
        defines = [f'-D{d}' for d in self.defines]
        warnings = [f'-W{l}' for l in self.warnings]

        result = subprocess.run([self.cxx, '-c', src, '-o', obj, *includes, *defines, *self.cxxflags, *warnings])

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, obj)
        
        return CompilationResult(True, 0, '', '', obj)
    
    def link(self, objs: List[str], dest: str, release=False, mwindows=False) -> CompilationResult:
        if dest != '' and not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        
        libdirs = [f'-L{l}' for l in self.libdirs]
        libs = [f'-l{l}' for l in self.libs]
        warnings = [f'-W{l}' for l in self.warnings]

        if mwindows:
            libs.append('-mwindows')

        cmd = [
            self.cxx,
            '-o', dest,
            *objs,
            *libdirs,
            *libs,
            *self.cxxflags,
            *warnings
        ]

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

        if not 'linker' in config:
            config['linker'] = {}

        if not 'cxx' in config['compiler'] or config['compiler']['cxx'] == '':
            print("No compiler set, defaulting to g++")
            config['compiler']['cxx'] = 'g++'

        if not 'standard' in config['compiler'] or config['compiler']['standard'] == '':
            print("No standard set, defaulting to c++17")
            config['compiler']['standard'] = 'c++17'
        
        includes = config['compiler'].get('includes', [])
        binaries = config['compiler'].get('binaries', [])
        defines = config['compiler'].get('defines', [])
        libdirs = config['linker'].get('libdirs', [])
        libs = config['linker'].get('libs', [])

        current_platform = platform.system().lower()

        if current_platform in config['compiler']:
            platform_config = config['compiler'][current_platform]
            includes += platform_config.get('includes', [])
            binaries += platform_config.get('binaries', [])
            defines += platform_config.get('defines', [])
        
        if current_platform in config['linker']:
            platform_config = config['linker'][current_platform]
            libdirs += platform_config.get('libdirs', [])
            libs += platform_config.get('libs', [])

        dep_repo = Repository()

        if 'requires' in config:
            deps = config.get('deps', {})
            for req in config['requires']:
                if req in deps or req in dep_repo:
                    dependencies = deps[req] if req in deps else dep_repo[req]
                    dependence = Dependence(req, dependencies, '.')
                    includes += dependence.includes
                    libdirs += dependence.libdirs
                    libs += dependence.libs
                    binaries += dependence.binaries
                    defines += dependence.defines
                
        return SourceCompiler(
            cxx=config['compiler']['cxx'],
            cxxflags=['-std=' + config['compiler']['standard']],
            includes=includes,
            libdirs=libdirs,
            libs=libs,
            binaries=binaries,
            defines=defines,
            warnings=config['compiler'].get('warnings', [])
        )