
import os

class Subprojects:
    def __init__(self, config: "Config", path: str):
        self.subprojects = {}
        self.config = config
        self.path = path

        if 'subprojects' in self.config.dict:
            self.subprojects = config.dict['subprojects']
    
    def compile(self):
        for name in self.subprojects:
            if not name in self.config.lockfile.subproject:
                self.config.lockfile.subproject[name] = { 'stamp': None }

            subproject = self.config.dict['subprojects'][name]
            subproject_lock = self.config.lockfile.subproject[name]
            path = os.path.join(self.path, name)

            if subproject_lock['stamp'] == None or subproject_lock['stamp'] < os.path.getmtime(path):
                self.compile_subproject(name, subproject)
                subproject_lock['stamp'] = os.path.getmtime(path)
                self.config.lockfile.save()
            else:
                print(f'Compiled subproject {name}')

    def compile_subproject(self, name: str, project: dict):
        if not 'path' in project:
            project['path'] = name
        
        path = os.path.join(self.path, project['path'])
        
        from plus.project import Project
        from plus.config import Config

        old_dir = os.getcwd()
        os.chdir(path)

        config = Config.from_file(os.path.join(path, 'plus.toml'))
        subproject = Project(path, config)
        subproject.compile()

        os.chdir(old_dir)

    def get_compiler_config(self):
        from plus.config import Config

        includes = []
        libs = []
        libdirs = []
        binaries = []
        defines = []

        for name in self.subprojects:
            subproject = self.subprojects[name]
            path = os.path.join(self.path, subproject['path'])
            config = Config.from_file(os.path.join(path, 'plus.toml'))
            compiler = config.dict.get('compiler', { })

            if 'linker' in config.dict and 'type' in config.dict['linker']:
                if config.dict['linker']['type'] == 'static-lib':
                    libs += [f'{name}']
                    libdirs += [os.path.join(path, 'lib')]
            
            includes += [os.path.join(path, f) for f in compiler.get('includes', [])]
            libs += compiler.get('libs', [])
            libdirs += [os.path.join(path, f) for f in compiler.get('libdirs', [])]
            binaries += [os.path.join(path, f) for f in compiler.get('binaries', [])]
            defines += compiler.get('defines', [])
        
        return {
            'includes': includes,
            'libs': libs,
            'libdirs': libdirs,
            'binaries': binaries,
            'defines': defines
        }

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