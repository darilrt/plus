import toml
import os

class LockFile:
    def __init__(self, path):
        self._path = path
        self.is_valid = False
        self.files = {}
        self.deps = {}
        
    def load(self):
        if os.path.exists(self._path):
            with open(self._path, 'r') as f:
                try:
                    data = toml.load(f)
                    self.is_valid = True
                except:
                    print('Invalid lock file')
                    self.is_valid = False
                    return
        else:
            self.is_valid = True
            return
        
        self.files = data.get('files', {})
        self.dependencies = data.get('deps', {})
    
    def save(self):
        with open(self._path, 'w') as f:
            toml.dump({
                'files': self.files,
                'deps': self.deps
            }, f)
    
    def add_file(self, file: str, object=None):
        self.files[file] = {
            'stamp': os.path.getmtime(file),
            'object': object
        }
    
    def get_file(self, file: str) -> dict:
        return self.files[file]