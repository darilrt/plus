
import subprocess
import toml
import os

class DepRepository:
    PLUS_REPO = 'http://github.com/darilrt/plus-deps.git'
    PLUS_HOME = os.path.join(os.path.expanduser("~"), '.plus')

    def __init__(self):
        self._deps = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.PLUS_HOME):
            os.mkdir(self.PLUS_HOME)

        if not os.path.exists(os.path.join(self.PLUS_HOME, 'deps.toml')):
            return

        with open(os.path.join(self.PLUS_HOME, 'deps.toml'), 'r') as f:
            data = toml.load(f)
            self._deps = data.get('deps', {})
    
    def upgrade(self):
        if not os.path.exists(self.PLUS_HOME):
            os.mkdir(self.PLUS_HOME)

        print('Updating dependencies...')

        if not os.path.exists(os.path.join(self.PLUS_HOME, 'deps.toml')):
            result = subprocess.run(['git', 'clone', self.PLUS_REPO, self.PLUS_HOME], capture_output=True)

            if result.returncode != 0:
                print('Failed to download dependencies')
                return
        
        result = subprocess.run(['git', 'pull'], cwd=self.PLUS_HOME, capture_output=True)

        if result.returncode != 0:
            print('Failed to update dependencies')
            return

        self._load()

        print('Done')
    
    def get(self, key: str, default: any) -> any:
        return self._deps.get(key, default)
    
    def set(self, key: str, value: any):
        self._deps[key] = value
    
    def __getitem__(self, key: str) -> any:
        return self.get(key, None)
    
    def __setitem__(self, key: str, value: any):
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        return key in self._deps
    
    def __str__(self) -> str:
        return str(self._deps)
