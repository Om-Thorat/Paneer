import inquirer
import subprocess
import shutil
import os
import pathlib
import sys
import argparse
import importlib.resources as resources
import PyInstaller.__main__

def get_templates_dir():
    return pathlib.Path(__file__).parent.absolute() / "templates"

def get_available_templates():
    templates_dir = get_templates_dir()
    if not templates_dir.exists():
        return []
    return [d.name.capitalize() for d in templates_dir.iterdir() if d.is_dir()]

def run_scaffolder(framework, project_name):
    template_path = get_templates_dir() / framework.lower()

    if not template_path.exists():
        print(f"Error: Template for {framework} not found.")
        return None

    print(f"Scaffolding {framework} project in {project_name}...")
    shutil.copytree(template_path, project_name)

    # Update package.json with project name
    pkg_json_path = os.path.join(project_name, "package.json")
    if os.path.exists(pkg_json_path):
        with open(pkg_json_path, "r") as f:
            content = f.read()
        content = content.replace("{{project_name}}", project_name)
        with open(pkg_json_path, "w") as f:
            f.write(content)

    npm_path = shutil.which("npm")
    if npm_path:
        print("Installing dependencies...")
        try:
            subprocess.run([npm_path, "install"], cwd=project_name, check=True)
        except subprocess.CalledProcessError:
            print("Warning: 'npm install' failed. You may need to run it manually.")
    else:
        print("Warning: 'npm' not found. Please run 'npm install' manually.")

    return framework

def run_build():
    npm_path = shutil.which("npm")
    if not npm_path:
        print("Error: 'npm' not found on PATH.")
        return

    print("Building frontend...")
    try:
        subprocess.run([npm_path, "run", "build"], check=True)
    except subprocess.CalledProcessError:
        print("Error: npm run build failed.")
        return

    print("Packaging with PyInstaller...")
    os.makedirs("release", exist_ok=True)
    sep = ";" if os.name == "nt" else ":"

    add_data_args = ["--add-data", f"dist{sep}dist"]
    
    try:
        paneer_root = resources.files("paneer")
        libs_path = paneer_root.joinpath("libs")
        if os.path.isdir(str(libs_path)):
            add_data_args += ["--add-data", f"{str(libs_path)}{sep}paneer/libs"]
    except Exception:
        pass

    PyInstaller.__main__.run([
        "--collect-all", "paneer",
        "--collect-submodules", "paneer",
        "--hidden-import", "paneer.windows",
        "--hidden-import", "paneer.linux",
        "--hidden-import", "clr",
        "main.py",
        *add_data_args,
        "--distpath", "release",
        "--noconfirm"
    ])
    print("Build complete! Check the 'release' directory.")

def main():
    parser = argparse.ArgumentParser(description="Paneer CLI: Build and scaffold projects easily.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    subparsers.add_parser("build", help="Build the application for release")
    subparsers.add_parser("run", help="Run the application in development mode")

    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("--framework", help="Framework to use")
    create_parser.add_argument("--project-name", help="Project name", default="my-paneer-app")

    args = parser.parse_args()

    if args.command == "build":
        run_build()

    elif args.command == "run":
        env = os.environ.copy()
        env['paneer_env'] = 'dev'
        npm_cmd = shutil.which("npm") or "npm"
        
        print("Starting development servers...")
        procs = [
            subprocess.Popen([npm_cmd, "run", "dev"], env=env),
            subprocess.Popen([sys.executable, "main.py"], env=env)
        ]
        try:
            for p in procs:
                p.wait()
        except KeyboardInterrupt:
            for p in procs:
                p.terminate()

    elif args.command == "create":
        available = get_available_templates()
        framework = args.framework
        project_name = args.project_name

        if framework not in available:
            print("(More frameworks coming soon!)")
            questions = [
                inquirer.List("framework", message="Select a frontend framework:", choices=available),
                inquirer.Text("project_name", message="Project name:", default=project_name),
            ]
            answers = inquirer.prompt(questions)
            if not answers: return
            framework = answers["framework"]
            project_name = answers["project_name"]

        if run_scaffolder(framework, project_name):
            try:
                example_py = pathlib.Path(__file__).parent / "patches" / "example.py"
                shutil.copy(example_py, os.path.join(project_name, "main.py"))
                print(f"\nSuccess! Project '{project_name}' is ready.")
                print(f"Next steps:\n  cd {project_name}\n  paneer run")
            except Exception as e:
                print(f"Error setting up main.py: {e}")

if __name__ == "__main__":
    main()