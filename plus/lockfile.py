import toml
import os

class LockFile:
    def __init__(self, path):
        self._path = path
        self.is_valid = False
        self.files = {}
        self.deps = {}
        self.subproject = {}
        
    def load(self):
        if os.path.exists(self._path):
            with open(self._path, 'r') as f:
                try:
                    data = toml.load(f)
                    self.is_valid = True
                except:
                    print('Invalid lockfile')
                    self.is_valid = False
                    return
        else:
            self.is_valid = True
            return
        
        self.files = data.get('files', {})
        self.deps = data.get('deps', {})
        self.subproject = data.get('subproject', {})
    
    def save(self):
        with open(self._path, 'w') as f:
            toml.dump({
                'files': self.files,
                'deps': self.deps,
                'subproject': self.subproject
            }, f)
    
    def add_file(self, file: str, object=None):
        self.files[file] = {
            'stamp': os.path.getmtime(file),
            'object': object
        }
    
    def add_dep(self, dep: str, stamp: str):
        self.deps[dep] = stamp

    def get_dep(self, dep: str) -> str:
        return self.deps[dep]
    
    def get_deps(self) -> dict:
        return self.deps
    
    def get_files(self) -> dict:
        return self.files
    
    def add_subproject(self, subproject: str, stamp: int):
        self.subproject[subproject] = { 'stamp': stamp }

    def get_subproject(self, subproject: str) -> dict:
        return self.subproject[subproject]
    
    def get_subprojects(self) -> dict:
        return self.subproject

    def in_subproject(self, subproject: str) -> bool:
        return subproject in self.subproject
    