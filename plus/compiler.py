import subprocess
import platform
import rich
import time
import os

class CompilerDeps:
    def __init__(self) -> None:
        self.include_dirs = []
        self.lib_dirs = []
        self.libs = []
        self.sources = []
        self.defines = []
        self.flags = []
        self.binaries = []

    def merge(self, deps: "CompilerDeps") -> None:
        self.include_dirs.extend(deps.include_dirs)
        self.lib_dirs.extend(deps.lib_dirs)
        self.libs.extend(deps.libs)
        self.defines.extend(deps.defines)
        self.sources.extend(deps.sources)
        self.binaries.extend(deps.binaries)

    def remove_duplicates(self) -> None:
        self.include_dirs = list(set(self.include_dirs))
        self.lib_dirs = list(set(self.lib_dirs))
        self.defines = list(set(self.defines))
        self.sources = list(set(self.sources))

class Compiler:
    ignore_projects = {}

    def __init__(self) -> None:
        self.cxx = "g++"
        self.c = "gcc"
        self.stdcxx = "c++20"
        self.std = "c11"
        self.deps = CompilerDeps()
        self.project = None
        self.subprojects: list = []
        self.objects = []
    
    def info(self) -> None:
        rich.print(f"C++ Compiler: [bold green]{self.cxx}[/bold green]")
        rich.print(f"C Compiler: [bold green]{self.c}[/bold green]")
        rich.print(f"Subprojects: [bold green]{self.subprojects}[/bold green]")

        bs = '\n'
        rich.print(f"Sources: \n[bold green]{bs.join(self.deps.sources)}[/bold green]")

        cmd: str = self._generate_cxx_cmd(self.deps.sources[0], self.deps.sources[0] + ".o")
        rich.print(f"Command: [bold green]{cmd}[/bold green]") 

    def compile(self, is_subproject: bool = False, wait_sp: bool = True) -> None:
        old_path: str = os.getcwd()
        os.chdir(self.project.path)

        if not os.path.exists('obj'):
            os.makedirs('obj')
        
        process: list[tuple[subprocess.Popen, str]] = []

        for sub in self.subprojects:
            self.deps.include_dirs.append(os.path.join(sub.path, "include"))
            
            if 'linker' in sub.config:
                linker = sub.config['linker']
                if 'type' in linker:
                    if linker['type'] == 'static-lib':
                        self.deps.lib_dirs.append(os.path.join(sub.path, "lib"))
                        self.deps.libs.append(sub.name)
                    elif linker['type'] == 'shared-lib':
                        self.deps.lib_dirs.append(os.path.join(sub.path, "lib"))
            
            if sub.name in self.ignore_projects:
                continue
            
            compiler = Compiler.from_project(sub)
            process.extend(compiler.compile(True, False))
            self.ignore_projects[sub.name] = compiler.objects

            self.deps.include_dirs.extend(compiler.deps.include_dirs)
            self.deps.lib_dirs.extend(compiler.deps.lib_dirs)
            self.deps.libs.extend(compiler.deps.libs)
            self.deps.defines.extend(compiler.deps.defines)
            self.deps.binaries.extend(compiler.deps.binaries)
        
        rich.print(f"Compiling {'subproject' if is_subproject else 'project'} [bold blue]{self.project.name}[/bold blue]")

        self.deps.remove_duplicates()

        for source in self.deps.sources:
            output: str = source.replace('src', 'obj') + ".o"
            cmd: str = self._generate_cxx_cmd(source, output)

            if source.replace('\\', '/') in self.project.lock:
                data: dict = self.project.lock[source.replace('\\', '/')]
                
                if os.path.exists(output) and 'mtime' in data:
                    if os.path.getmtime(source) <= data['mtime']:
                        self.objects.append(output)
                        continue
            
            self.objects.append(output)

            basedir: str = os.path.dirname(output)

            if not os.path.exists(basedir):
                os.makedirs(basedir)

            rich.print(f"    [bold yellow]Compiling[/bold yellow] [bold green]{source}[/bold green]")

            process.append((
                subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE),
                source,
                cmd,
                os.path.getmtime(source),
                self.project,
                time.time()
            ))

        bin_path: str = os.path.join(self.project.path, "bin")
        if not os.path.exists(bin_path):
            os.makedirs(bin_path)
        
        lib_path: str = os.path.join(self.project.path, "lib")
        if not os.path.exists(lib_path):
            os.makedirs(lib_path)

        if wait_sp:
            console = rich.console.Console()

            with console.status("[bold green]Compiling[/bold green]", spinner="simpleDots") as status:
                ready: int = 0
                total: int = len(process)

                while ready < total:
                    for i in range(len(process)):
                        item: tuple[subprocess.Popen, str, str, float, "Project"] = process[i]
                        ret: int = item[0].poll()

                        _t: float = time.time() - item[5]

                        if _t > 10:
                            console.line()
                            console.print(f"[bold red]Error[/bold red] in process code [bold green]{ret}[/bold green]")
                            console.print(f'    [bold green]{item[2]}[/bold green]')
                            console.print(f'on file')
                            console.print(f'    [bold green]{item[1]}[/bold green]')
                            item[0].terminate()
                            console.print(item[0].stdout.read().decode('utf-8'))
                            console.print(item[0].stderr.read().decode('utf-8'))
                            exit(1)

                        if ret is not None and ret == 0:
                            ready += 1

                            item[4].lock[item[1].replace('\\', '/')] = {
                                "mtime": item[3]
                            }
                            item[4].save_lock()

                            process.pop(i)
                            break
                        elif ret is not None and ret != 0:
                            console.line()
                            console.print(f"[bold red]Error[/bold red] in process code [bold green]{ret}[/bold green]")
                            console.print(f'    [bold green]{item[2]}[/bold green]')
                            console.print(f'on file')
                            console.print(f'    [bold green]{item[1]}[/bold green]')
                            item[0].terminate()
                            console.print(item[0].stdout.read().decode('utf-8'))
                            console.print(item[0].stderr.read().decode('utf-8'))
                            exit(1)

                    status.update(f"[bold green]Compiling[/bold green] {ready}/{total}")

            _links: list[str] = self.get_linkers()
            links: list[str] = []

            for link in _links:
                if link not in links:
                    links.append(link)

            rich.print(f"Linking")

            with console.status("[bold green]Linking[/bold green]", spinner="simpleDots") as status:
                total: int = len(links)
                while True:
                    if len(links) <= 0:
                        break

                    link: str = links.pop(0)
                    result: subprocess.CompletedProcess[bytes] = subprocess.run(link, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    status.update(f"[bold green]Linking[/bold green] {total - len(links)}/{total}")

                    if result.returncode != 0:
                        console.line()
                        console.print(f"[bold red]Error[/bold red] in process code [bold green]{result.returncode}[/bold green]")
                        console.print(f'    [bold green]{link}[/bold green]')
                        console.print(result.stdout.decode('utf-8'))
                        console.print(result.stderr.decode('utf-8'))
                        exit(1)
                    
            rich.print(f"Project [bold blue]{self.project.name}[/bold blue] compiled")

            for binary in self.deps.binaries:
                if os.path.exists(binary):
                    os.system(f"cp {binary} {os.path.join(self.project.path, 'bin')}")

            os.chdir(old_path)
            return os.path.join(self.project.path, "bin", self.project.name)

        os.chdir(old_path)
        return process
    
    def get_linkers(self) -> list[str]:
        linkers: list[str] = []

        for sub in self.subprojects:
            compiler = Compiler.from_project(sub)
            
            for t in compiler.get_linkers():
                linkers.append(t)
        
        objs: list[str] = []

        for src in self.deps.sources:
            objs.append(src.replace('src', 'obj') + ".o")

        cmd: str = self._generate_link_cmd(objs, os.path.join(self.project.path, "bin", self.project.name))
        if cmd:
            linkers.append(cmd)
        
        return linkers
    
    def _generate_cxx_cmd(self, source: str, output: str) -> str:
        includes: str = " ".join([f"-I{inc}" for inc in self.deps.include_dirs])
        libdirs: str = " ".join([f"-L{lib}" for lib in self.deps.lib_dirs])
        libs: str = " ".join([f"-l{lib}" for lib in self.deps.libs])
        defines: str = " ".join([f"-D{defn}" for defn in self.deps.defines])

        return f"{self.cxx} -std={self.stdcxx} {includes} {libdirs} {libs} {defines} -c {source} -o {output} ".replace("\\", "/")

    def _generate_link_cmd(self, sources: list[str], output: str) -> str:
        libdirs: str = " ".join([f"-L{lib}" for lib in self.deps.lib_dirs])
        libs: list[str] = [f"-l{lib}" for lib in self.deps.libs]
        defines: str = " ".join([f"-D{defn}" for defn in self.deps.defines])
        
        libs = " ".join(libs)
        
        if not 'linker' in self.project.config:
            return ""
        
        if 'type' in self.project.config['linker']:
            type: str = self.project.config['linker']['type']

            if type == 'shared-lib':
                output = os.path.join(self.project.path, "lib", self.project.name + {
                    "Windows": ".dll",
                    "Linux": ".so",
                    "Darwin": ".dylib"
                }[platform.system()])
                return f"{self.cxx} -shared {' '.join(sources)} -o {output} {libdirs} {libs} {defines}".replace("\\", "/")
            elif type == 'static-lib':
                output = os.path.join(self.project.path, "lib", self.project.name + {
                    "Windows": ".lib",
                    "Linux": ".a",
                    "Darwin": ".a"
                }[platform.system()])
                return f"ar rcs {output} {' '.join(sources)}".replace("\\", "/")
            elif type == 'console-app':
                output = os.path.join(self.project.path, "bin", self.project.name + {
                    "Windows": ".exe",
                    "Linux": "",
                    "Darwin": ""
                }[platform.system()])
                return f"{self.cxx} {' '.join(sources)} -o {output} {defines} {libdirs} {libs}".replace("\\", "/")

        return ""

    @staticmethod
    def from_project(project: "Project") -> "Compiler":
        compiler = Compiler()
        compiler.deps = project.get_compiler_deps()
        compiler.project = project
        compiler.subprojects = project.get_subprojects()

        if 'compiler' in project.config:

            if 'cxx' in project.config['compiler']:
                compiler.cxx = project.config['compiler']['cxx']

            if 'c' in project.config['compiler']:
                compiler.c = project.config['compiler']['c']
        
            if 'standard' in project.config['compiler']:
                compiler.stdcxx = project.config['compiler']['standard']

        return compiler