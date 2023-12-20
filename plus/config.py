import toml
import os

class Config:
    def __init__(self, path: str, type="console-app"):
        self.is_valid = True
        self._path = path
        self._config = {
            "project": {
                "name": "<name>",
                "version": "0.1.0",
                "description": "",
                "author": "",
                "email": "",
                "url": "",
                "license": "",
            },
            "compiler": {
                "type": type,
                "cxx": "g++",
                "standard": "c++17",
                "includes": [ "include" ],
                "libdirs": [],
                "libs": [],
            },
            "requires": {},
        }

        if os.path.exists(self._path):
            self.load()
    
    def load(self):
        with open(self._path, 'r') as f:
            try:
                self._config = toml.load(f)
                self.is_valid = True
            except toml.decoder.TomlDecodeError as e:
                print("Error loading", self._path)
                print(e)
                self.is_valid = False
    
    def save(self):
        with open(self._path, 'w') as f:
            f.write(toml.dumps(self._config))
    
    def get(self, key: str, default: any) -> any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: any):
        self._config[key] = value
    
    def __getitem__(self, key: str) -> any:
        return self.get(key, None)
    
    def __setitem__(self, key: str, value: any):
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        return key in self._config
    
    def __str__(self) -> str:
        return str(self._config)