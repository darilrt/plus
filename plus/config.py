import json
import os

class Config:
    def __init__(self, path: str, type="console-app"):
        self.is_valid = True
        self._path = path
        self._config = {
            "version": "0.1.0",
            "description": "",
            "author": "",
            "email": "",
            "url": "",
            "license": "",
            "name": "<name>",
            "type": type,
            "compiler": "g++",
            "standard": "c++17",
            "includes": [],
            "libdirs": [],
            "libs": [],
            "requires": [],
            "dependencies": {}
        }

        if os.path.exists(self._path):
            self.load()
    
    def load(self):
        with open(self._path, 'r') as f:
            try:
                self._config = json.load(f)
                self.is_valid = True
            except json.decoder.JSONDecodeError as e:
                print("Error loading", self._path)
                print(e)
                self.is_valid = False
    
    def save(self):
        with open(self._path, 'w') as f:
            f.write(json.dumps(self._config, indent=4))
    
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