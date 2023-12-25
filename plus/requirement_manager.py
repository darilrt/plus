from pathlib import Path

import os
import platform
import shutil
import stat
import subprocess

from plus.repository import Repository
from plus.rtext import *

def rmdir(path: str):
    def readonly_to_writable(foo, file, err):
        if Path(file).suffix in ['.idx', '.pack'] and 'PermissionError' == err[0].__name__:
            os.chmod(file, stat.S_IWRITE)
            foo(file)

    shutil.rmtree(path, onerror=readonly_to_writable)
    
class Requirment:
    def __init__(self: "Requirment", name: str, config: "Config", root_config: "Config") -> None:
        self.name = name
        self.config = config
        self.root_config = root_config

        from plus.project import Project
        self.project = Project(f"vendor/{name}", config)
    
    def compile(self: "Requirment", force=False) -> None:
        if not force and self.is_compiled():
            return

        if os.path.exists(self.project.fullpath):
            rmdir(self.project.fullpath)
        
        if 'git' in self.config.dict:
            print(f"Cloning {rtext(self.name, color=color.green, style=style.bold)}")
            result = subprocess.run(['git', 'clone', '--depth', '1', self.config.dict['git'], self.project.path])
            if result.returncode != 0:
                exit(f"Failed to clone {rtext(self.name, color=color.green, style=style.bold)}")

        print(f"Bulding {rtext(self.name, color=color.green, style=style.bold)}")
        self.project.compile(optional_compile=True, root_config=self.root_config)
        self.root_config.lockfile.add_dep(self.name, os.path.getmtime(self.project.fullpath))
        self.root_config.lockfile.save()
    
    def is_compiled(self: "Requirment") -> bool:
        if not os.path.exists(self.project.fullpath):
            return False

        if self.name not in self.root_config.lockfile.get_deps():
            if os.path.exists(self.project.fullpath):
                rmdir(self.project.fullpath)

            return False

        stamp = self.root_config.lockfile.get_dep(self.name)
        return os.path.getmtime(self.project.fullpath) == stamp

class RequirementManager:
    def __init__(self: "RequirementManager", config: "Config", ignore_deps=[], root_config=None) -> None:
        self.config = config
        self.requirements = []

        self._includes = []
        self._libs = []
        self._libdirs = []
        self._binaries = []
        self._defines = []

        self._load(ignore_deps=ignore_deps, root_config=root_config)

    def list(self: "RequirementManager") -> None:
        print("Dependencies:")
        for req in self.requirements:
            print(f"  {rtext(req.name, color=color.green, style=style.bold)}")

    def add(self: "RequirementManager", name: str) -> None:
        if name in self.config.dict['require']:
            exit(f"Dependency {rtext(name, color=color.green, style=style.bold)} already exists")
        
        if 'deps' in self.config.dict:
            if name in self.config.dict['deps']:
                self.config.dict['require'].append(name)
        
        else:
            repo = Repository()
            if name in repo:
                self.config.dict['require'].append(name)
            else:
                exit(f"Could not resolve dependency {rtext(name, color=color.green, style=style.bold)}")

        self.config.save()

    def _load(self: "RequirementManager", ignore_deps=[], root_config=None) -> None:
        if 'require' in self.config.dict:
            repo = Repository()

            for name in self.config.dict['require']:
                if name in ignore_deps:
                    continue

                path = f"vendor/{name}"

                from plus.config import Config
                config = Config()
                if 'deps' in self.config.dict and name in self.config.dict['deps']:
                    config.dict = self.config.dict['deps'][name].copy()
                elif root_config and 'deps' in root_config.dict and name in root_config.dict['deps']:
                    config.dict = root_config.dict['deps'][name].copy()
                elif name in repo:
                    config.dict = repo[name].copy()
                else:
                    exit(f"Dependency {rtext(name, color=color.green, style=style.bold)} does not exist")
                
                config.name = name
                config.cxx = self.config.cxx
                config.standard = self.config.standard
                
                if 'compiler' in config.dict:
                    path = f"vendor/{name}"
                    config.dict['compiler']['includes'] = [f"{path}/{i}" for i in config.dict['compiler'].get('includes', [])]
                    config.dict['compiler']['libdirs'] = [f"{path}/{l}" for l in config.dict['compiler'].get('libdirs', [])]
                    config.dict['compiler']['binaries'] = [f"{path}/{b}" for b in config.dict['compiler'].get('binaries', [])]

                    config.dict['compiler']['windows'] = config.dict['compiler'].get('windows', {})
                    config.dict['compiler']['windows']['includes'] = [f"{path}/{i}" for i in config.dict['compiler']['windows'].get('includes', [])]
                    config.dict['compiler']['windows']['libdirs'] = [f"{path}/{l}" for l in config.dict['compiler']['windows'].get('libdirs', [])]
                    config.dict['compiler']['windows']['binaries'] = [f"{path}/{b}" for b in config.dict['compiler']['windows'].get('binaries', [])]

                    # TODO: Linux and Mac

                includes = config.dict.get('includes', [])
                libs = config.dict.get('libs', [])
                libdirs = config.dict.get('libdirs', [])
                binaries = config.dict.get('binaries', [])
                defines = config.dict.get('defines', [])
                
                current_platform = platform.system().lower()

                if current_platform in config.dict:
                    platform_config = config.dict[current_platform]
                    includes += platform_config.get('includes', [])
                    libs += platform_config.get('libs', [])
                    libdirs += platform_config.get('libdirs', [])
                    binaries += platform_config.get('binaries', [])
                    defines += platform_config.get('defines', [])
                
                self._includes += [f"{path}/{i}" for i in includes]
                self._libs += libs
                self._libdirs += [f"{path}/{l}" for l in libdirs]
                self._binaries += [f"{path}/{b}" for b in binaries]
                self._defines += defines

                self.requirements.append(Requirment(name, config, self.config))

    @property
    def includes(self: "RequirementManager") -> list:
        return self._includes
    
    @property
    def libs(self: "RequirementManager") -> list:
        return self._libs

    @property
    def libdirs(self: "RequirementManager") -> list:
        return self._libdirs

    @property
    def binaries(self: "RequirementManager") -> list:
        return self._binaries

    @property
    def defines(self: "RequirementManager") -> list:
        return self._defines

    def __iter__(self: "RequirementManager"):
        return iter(self.requirements)