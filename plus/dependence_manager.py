from plus.repository import Repository

class DependenceManager:
    def __init__(self, project_path: str) -> None:
        self.project_path = project_path
        self.vendor_path = os.path.join(project_path, 'vendor')
        self.lockfile = Lockfile(os.path.join(project_path, 'plus.lock'))
        self.repository = Repository()

    def require(self, name: str) -> None:
        dep = self.repository[name]

        if not dep:
            print(f'Package {name} not found')
            return
        
        print(f'Installing {name}...')