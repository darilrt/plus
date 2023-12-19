import os
import platform
import shutil
import subprocess
import sys

class Dependence:
    def __init__(self, name: str, info: dict, path: str):
        self._info = info
        self.name = name
        self.path = path
        self.includes = info["compiler"].get('includes', [])
        self.libdirs = info["compiler"].get('libdirs', [])
        self.libs = info["compiler"].get('libs', "")
        self.binaries = info["compiler"].get('binaries', [])
        self.defines = info["compiler"].get('defines', [])

        self.override_by_platform()
        self.normalize_paths()
    
    def override_by_platform(self):
        current_platform = platform.system().lower()

        if not current_platform in self._info:
            return
    
        info = self._info[current_platform]

        self.includes = info.get('includes', self.includes)
        self.libdirs = info.get('libdirs', self.libdirs)
        self.libs = info.get('libs', self.libs)
        self.binaries = info.get('binaries', self.binaries)
    
    def normalize_paths(self):
        vendor_path = os.path.join(self.path, 'vendor', self.name)
        
        self.includes = [os.path.join(vendor_path, i) for i in self.includes]
        self.libdirs = [os.path.join(vendor_path, l) for l in self.libdirs]
        self.binaries = [os.path.join(vendor_path, b) for b in self.binaries]

    def resolve(self):
        current_platform = platform.system().lower()

        build = self._info.get('build', [])

        if current_platform in self._info:
            build = self._info[current_platform].get('build', build)

        if not isinstance(build, list):
            build = [build]
            
        oldcwd = os.getcwd()

        os.chdir(self.path)
        if not os.path.exists('vendor'):
            os.mkdir('vendor')
        os.chdir('vendor')
        shutil.rmtree(self.name, ignore_errors=True)
        os.mkdir(self.name)
        os.chdir(self.name)

        for step in build:
            try:
                result = subprocess.run(step, shell=True, check=True)
                if result.returncode != 0:
                    exit(result.returncode)
            except subprocess.CalledProcessError as e:
                exit(e)

        print('\033[32m\u2713\033[0m built', self.name)

        os.chdir(oldcwd)