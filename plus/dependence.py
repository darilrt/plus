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
        self.includes = info.get('includes', [])
        self.libdirs = info.get('libdirs', [])
        self.bins = info.get('bins', [])
        self.libs = info.get('libs', "")
        self.dlls = info.get('dlls', [])

        vendor_path = os.path.join(path, 'vendor', name)

        self.includes = [os.path.join(vendor_path, i) for i in self.includes]
        self.libdirs = [os.path.join(vendor_path, l) for l in self.libdirs]
        self.bins = [os.path.join(vendor_path, b) for b in self.bins]

    def resolve(self):
        if (builds := [k for k,v in self._info.items() if 'build+' in k]):
            for build in builds:
                self._build(build)
        
        if 'build' in self._info:
            self._build('build')
    
    def _build(self, build: str):
        _platform = 'universal'

        if build.startswith('build+'): # platform specific
            _platform = build.split('+')[1]

        elif build != 'build':
            exit('Invalid build type ' + build)

        current_platform = platform.system().lower()

        if _platform != 'universal' and _platform != current_platform:
            exit('Platform ' + current_platform + ' is not supported')

        oldcwd = os.getcwd()

        os.chdir(self.path)
        if not os.path.exists('vendor'):
            os.mkdir('vendor')
        os.chdir('vendor')
        shutil.rmtree(self.name, ignore_errors=True)
        os.mkdir(self.name)
        os.chdir(self.name)

        for step in self._info[build]:
            try:
                result = subprocess.run(step, shell=True, check=True)
                if result.returncode != 0:
                    exit(result.returncode)
            except subprocess.CalledProcessError as e:
                exit(e)

        print('\033[32m\u2713\033[0m built', self.name)

        os.chdir(oldcwd)