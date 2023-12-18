import json
import os

class Config:
    def __init__(self, path, type="console-app"):
        self.is_valid = True
        self._path = path
        self._config = {
            "name": "<name>",
            "type": type,
            "version": "0.1.0",
            "description": "",
            "author": "",
            "email": "",
            "url": "",
            "license": "",
            "compiler": "g++",
            "standard": "c++17",
            "dependencies": []
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
    
    def get(self, key):
        return self._config[key]
    
    def set(self, key, value):
        self._config[key] = value
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __setitem__(self, key, value):
        self.set(key, value)
    
    def __contains__(self, key):
        return key in self._config
    
    def __str__(self):
        return str(self._config)