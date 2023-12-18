from typing import List
from .config import Config
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
    def __init__(self, cxx='', cxxflags=[], libs=[], includes=[]):
        self.cxx = cxx
        self.cxxflags = cxxflags
        self.libs = libs
        self.includes = includes

    def compile(self, src: str, dest: str, release=False) -> CompilationResult:
        if not os.path.exists(dest):
            os.mkdir(dest)
        
        obj = os.path.join(dest, os.path.splitext(os.path.basename(src))[0] + '.o')

        result = subprocess.run([self.cxx, *self.cxxflags, *self.includes, '-c', src, '-o', obj])

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, obj)
        
        return CompilationResult(True, 0, '', '', obj)
    
    def link(self, objs: List[str], dest: str, release=False) -> CompilationResult:
        result = subprocess.run([self.cxx, *self.cxxflags, *self.libs, '-o', dest, *objs])

        if result.returncode != 0:
            return CompilationResult(False, result.returncode, result.stderr, result.stdout, dest)
        
        return CompilationResult(True, 0, '', '', dest)

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
        
        includes = []

        if 'includes' in config:
            includes = config['includes']
        
        libs = []

        if 'libs' in config:
            libs = config['libs']
        
        return SourceCompiler(
            cxx=config['compiler'],
            cxxflags=['-std=' + config['standard'], '-Wall', '-Wextra', '-pedantic'],
            libs=libs,
            includes=includes
        )