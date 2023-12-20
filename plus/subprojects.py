
from .config import Config
from .lockfile import LockFile
import os

class Subprojects:
    def __init__(self, config: Config, lockfile: LockFile, path: str):
        self.subprojects = []
        self.config = config
        self.lockfile = lockfile
        self.path = path

        if 'subprojects' in config:
            self.subprojects = config['subprojects']
    
    def build(self):
        for name in self.subprojects:
            if not name in self.lockfile.subproject:
                self.lockfile.subproject[name] = { 'stamp': None }

            subproject = self.config['subprojects'][name]
            subproject_lock = self.lockfile.subproject[name]
            path = os.path.join(self.path, name)

            if subproject_lock['stamp'] == None or subproject_lock['stamp'] < os.path.getmtime(path):
                self.build_subproject(name, subproject)
                subproject_lock['stamp'] = os.path.getmtime(path)
                self.lockfile.save()
            else:
                print(f'Compiled subproject {name}')

    def build_subproject(self, name: str, project: dict):
        if not 'path' in project:
            project['path'] = name
        
        path = os.path.join(self.path, project['path'])
        
        from .project import Project

        subproject = Project(path)
        subproject.validate()
        subproject.build()
        
    def get_include_dirs(self):
        includes = []

        for subproject in self.subprojects:
            includes.extend(subproject.get_include_dirs())
        
        return includes

    def __iter__(self):
        return iter(self.subprojects)

    def __len__(self):
        return len(self.subprojects)

    def __getitem__(self, key):
        return self.subprojects[key]
    
    def __setitem__(self, key, value):
        self.subprojects[key] = value

    def __delitem__(self, key):
        del self.subprojects[key]

    def __contains__(self, item):
        return item in self.subprojects
    
    def __str__(self):
        return str(self.subprojects)