import subprocess
import toml
import rich
import os

PLUS_HOME = os.path.join(os.path.expanduser("~"), '.plus')

class Repository:
    PLUS_REPO = 'http://github.com/darilrt/plus-deps.git'

    _deps = {}

    @staticmethod
    def load():
        if not os.path.exists(PLUS_HOME):
            os.mkdir(PLUS_HOME)

        if not os.path.exists(os.path.join(f"{PLUS_HOME}/deps", 'deps.toml')):
            Repository.upgrade()
            return

        with open(os.path.join(f"{PLUS_HOME}/deps", 'deps.toml'), 'r') as f:
            data = toml.load(f)
            Repository._deps = data.get('deps', {})
    
    @staticmethod
    def upgrade() -> None:
        if not os.path.exists(PLUS_HOME):
            os.mkdir(PLUS_HOME)

        print('Updating dependencies...')

        if not os.path.exists(os.path.join( f"{PLUS_HOME}/deps", 'deps.toml')):
            result = subprocess.run(['git', 'clone', Repository.PLUS_REPO, f"{PLUS_HOME}/deps"], capture_output=True)

            if result.returncode != 0:
                print('Failed to download dependencies')
                return
        
        result = subprocess.run(['git', 'pull'], cwd=f"{PLUS_HOME}/deps", capture_output=True)

        if result.returncode != 0:
            print('Failed to update dependencies')
            return

        Repository.load()

        rich.print('Dependencies updated')

    @staticmethod
    def get(key: str) -> any:
        return Repository._deps[key]

    @staticmethod
    def has(key: str) -> bool:
        return key in Repository._deps