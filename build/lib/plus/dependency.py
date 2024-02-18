from plus.compiler import CompilerDeps
import platform
import rich
import os

class Dependency:
    def __init__(self) -> None:
        self.name: str = ""
        self.git: str = None
        self.pre_build: list[str] = []
        self.deps: CompilerDeps = CompilerDeps()

    def get_compiler_deps(self, path: str) -> CompilerDeps:
        deps: CompilerDeps = CompilerDeps()

        deps.include_dirs = [os.path.join(path, self.name, inc) for inc in self.deps.include_dirs]
        deps.lib_dirs = [os.path.join(path, self.name, lib) for lib in self.deps.lib_dirs]
        deps.libs = self.deps.libs
        deps.defines = self.deps.defines
        deps.flags = self.deps.flags
        deps.binaries = [os.path.join(path, self.name, bin) for bin in self.deps.binaries]

        return deps
    
    def install(self, path: str) -> None:
        folder: str = os.path.join(path, self.name)

        if not os.path.exists(folder):
            os.makedirs(folder)
        
        if self.git is not None:
            os.system(f"git clone --depth 1 {self.git} {folder}")
        
        old_dir = os.getcwd()
        os.chdir(folder)

        for cmd in self.pre_build:
            os.system(cmd)

        os.chdir(old_dir)

    @staticmethod
    def from_dict(data: dict, name: str) -> "Dependency":
        dep = Dependency()

        dep.name = name
        dep.git = data.get('git', None)

        dep.deps.include_dirs = data.get('includes', [])    
        dep.deps.defines = data.get('defines', [])
        dep.deps.lib_dirs = data.get('libdirs', [])
        dep.deps.libs = data.get('libs', [])
        dep.deps.binaries = data.get('binaries', [])
        
        plat: str = platform.system().lower()

        if plat in data:
            plat_data = data[plat]

            if 'includes' in plat_data:
                dep.deps.include_dirs = plat_data.get('includes', [])
            
            if 'defines' in plat_data:
                dep.deps.defines = plat_data.get('defines', [])
            
            if 'libdirs' in plat_data:
                dep.deps.lib_dirs = plat_data.get('libdirs', [])
            
            if 'libs' in plat_data:
                dep.deps.libs = plat_data.get('libs', [])

            if 'binaries' in plat_data:
                dep.deps.binaries = plat_data.get('binaries', [])

            if 'pre-build' in plat_data:
                dep.pre_build = plat_data['pre-build']

        return dep
