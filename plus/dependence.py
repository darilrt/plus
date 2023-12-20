import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess

def rmdir(path: str):
    def readonly_to_writable(foo, file, err):
        if Path(file).suffix in ['.idx', '.pack'] and 'PermissionError' == err[0].__name__:
            os.chmod(file, stat.S_IWRITE)
            foo(file)

    shutil.rmtree(path, onerror=readonly_to_writable)

def cd_and_mkdir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

class Dependence:
    def __init__(self, name: str, info: dict, path: str):
        self._info = info
        self.name = name
        self.path = path
        self.git = info.get('git', None)
        self.includes = info.get('includes', [])
        self.libdirs = info.get('libdirs', [])
        self.libs = info.get('libs', "")
        self.binaries = info.get('binaries', [])
        self.defines = info.get('defines', [])

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
        if self.git:
            self._resolve_git()
        else:
            self._resolve_build()

        current_platform = platform.system().lower()

        build = self._info.get('build', [])

        if current_platform in self._info:
            build = self._info[current_platform].get('build', build)

        if not isinstance(build, list):
            build = [build]
            
        oldcwd = os.getcwd()

        if self.git:
            os.chdir(self.path + '/vendor/' + self.name)

        else:    
            cd_and_mkdir(self.path + '/vendor')
            rmdir(self.name)
            if not os.path.exists(self.name):
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
    
    def _resolve_git(self):
        if not shutil.which('git'):
            print('\033[31m\u2717\033[0m git not found')
            exit(1)
        
        oldcwd = os.getcwd()

        cd_and_mkdir(self.path + '/vendor')
        print(self.path + '/vendor')
        rmdir(self.name)

        result = subprocess.run(['git', 'clone', self.git, self.name])

        if result.returncode != 0:
            print('\033[31m\u2717\033[0m failed to clone', self.name)
            exit()

        os.chdir(self.name)

        print('\033[32m\u2713\033[0m cloned', self.name)

        os.chdir(oldcwd)

    def _resolve_build(self):
        pass