import subprocess
import os

class SourceCompiler:
    def __init__(self, cxx='', cxxflags=[], libs=[], includes=[]):
        self.cxx = cxx
        self.cxxflags = cxxflags
        self.libs = libs
        self.includes = includes

    def compile(self, src, dest, release=False):
        if not os.path.exists(dest):
            os.mkdir(dest)
        
        obj = os.path.join(dest, os.path.splitext(os.path.basename(src))[0] + '.o')

        result = subprocess.run([self.cxx, *self.cxxflags, *self.includes, '-c', src, '-o', obj])

        if result.returncode != 0:
            return (False, result.returncode, result.stderr, result.stdout, obj)
        
        return (True, 0, '', '', obj)
    
    def link(self, objs, dest, release=False):
        result = subprocess.run([self.cxx, *self.cxxflags, *self.libs, '-o', dest, *objs])

        if result.returncode != 0:
            return (False, result.returncode, result.stderr, result.stdout, dest)
        
        return (True, 0, '', '', dest)

    @staticmethod
    def from_config(config):
        if not 'compiler' in config or config['compiler'] == '':
            print("No compiler set, defaulting to g++")
            config['compiler'] = 'g++'
            config.save()

        if not 'standard' in config or config['standard'] == '':
            print("No standard set, defaulting to c++17")
            config['standard'] = 'c++17'
            config.save()
        
        return SourceCompiler(
            cxx=config['compiler'],
            cxxflags=['-std=' + config['standard'], '-Wall', '-Wextra', '-pedantic'],
            libs=[],
            includes=[]
        )