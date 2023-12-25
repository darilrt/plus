import toml

from plus.lockfile import LockFile
from plus.requirement_manager import RequirementManager

class Config:
    def __init__(self: "Config", name: str="<name>", type="console-app"):
        self.dict = self._get_default_dict(name, type)
        self.lockfile = LockFile("plus.lock")

    def save(self: "Config", path: str="plus.toml"):
        try:
            with open(path, "w") as f:
                toml.dump(self.dict, f)
        except Exception as e:
            exit(f"Could not save config file at {path}\n{e}")

    def get_requirement_manager(self: "Config", ignore_deps=[], root_config=None) -> RequirementManager:
        return RequirementManager(self, ignore_deps=ignore_deps, root_config=root_config)

    @property
    def type(self: "Config") -> str:
        if "type" not in self.dict["linker"]:
            exit("plus.toml file does not have a linker type\n[linker]\ntype = \"console-app\"")
        return self.dict["linker"]["type"]
    
    @type.setter
    def type(self: "Config", value: str) -> None:
        self.dict["linker"]["type"] = value

    @property
    def name(self: "Config") -> str:
        if "name" not in self.dict["project"]:
            exit("plus.toml file does not have a project name\n[project]\nname = \"<name>\"")
        return self.dict["project"]["name"]
    
    @name.setter
    def name(self: "Config", value: str) -> None:
        if 'project' not in self.dict:
            self.dict['project'] = { }
        self.dict["project"]["name"] = value

    @property
    def cxx(self: "Config") -> str:
        if 'compiler' not in self.dict:
            self.dict['compiler'] = { }
        if 'cxx' not in self.dict['compiler']:
            self.dict['compiler']['cxx'] = 'g++'
            print("plus.toml file does not have a compiler set, defaulting to g++")
        return self.dict["compiler"]["cxx"]
    
    @cxx.setter
    def cxx(self: "Config", value: str) -> None:
        if 'compiler' not in self.dict:
            self.dict['compiler'] = { }
        self.dict["compiler"]["cxx"] = value

    @property
    def standard(self: "Config") -> str:
        if 'compiler' not in self.dict:
            self.dict['compiler'] = { }
        if "standard" not in self.dict["compiler"]:
            self.dict["compiler"]["standard"] = "c++17"
            print("plus.toml file does not have a compiler standard set, defaulting to c++17")
        return self.dict["compiler"]["standard"]
    
    @standard.setter
    def standard(self: "Config", value: str) -> None:
        if 'compiler' not in self.dict:
            self.dict['compiler'] = { }
        self.dict["compiler"]["standard"] = value
    
    @property
    def debug(self: "Config") -> bool:
        if 'compiler' not in self.dict:
            self.dict['compiler'] = { }
        if 'debug' not in self.dict['compiler']:
            self.dict['compiler']['debug'] = True
        return self.dict["compiler"]["debug"]

    @staticmethod
    def from_file(path: str) -> "Config":
        config = Config()

        try:
            with open(path, "r") as f:
                config.dict = toml.load(f)
        except FileNotFoundError as e:
            exit(f"Could not find config file at {path}")
        except toml.TomlDecodeError as e:
            exit(f"Could not parse config file at {path}\n{e}")
        except Exception as e:
            exit(f"Could not load config file at {path}\n{e}")

        config.lockfile.load()

        return config

    @staticmethod
    def create(name: str, type="console-app") -> "Config":
        config = Config(name, type)
        config.save()
        return config

    def _get_default_dict(self: "Config", name: str, type="console-app") -> dict:
        return {
            "project": {
                "name": name,
                "version": "0.1.0",
                "description": "",
                "author": "",
                "email": "",
                "url": "",
                "license": "",
            },
            "compiler": {
                "cxx": "g++",
                "standard": "c++17",
                "flags": [ ],
                "includes": [ "include" ],
                "defines": [ ],
                "warnings": [ ],
                "debug": True,
            },
            "linker": {
                "type": type,
                "flags": [ ],
                "libdirs": [ ],
                "libs": [ ],
            },
            "require": [ ],
        }