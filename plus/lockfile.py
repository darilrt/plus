import json
import os

class LockFile:
    def __init__(self, path):
        self._path = path
        self.is_valid = False
        self.files = {}
        self.dependencies = {}
        
    def load(self):
        if os.path.exists(self._path):
            with open(self._path, 'r') as f:
                try:
                    data = json.load(f)
                    self.is_valid = True
                except:
                    print('Invalid lock file')
                    self.is_valid = False
                    return
        else:
            self.is_valid = True
            return
        
        self.files = data['files']
        self.dependencies = data['dependencies']
    
    def save(self):
        with open(self._path, 'w') as f:
            json.dump({
                'files': self.files,
                'dependencies': self.dependencies
            }, f, indent=4)
    
    def add_file(self, file: str, object=None):
        self.files[file] = {
            'stamp': os.path.getmtime(file),
            'object': object
        }
    
    def get_file(self, file: str) -> dict:
        return self.files[file]