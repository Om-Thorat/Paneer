import inquirer
import subprocess
from subprocess import Popen
import shutil
import os
import pathlib
import sys
import argparse
import importlib.resources as resources
import PyInstaller.__main__

def run_scaffolder(framework, project_name):

    script_dir = pathlib.Path(__file__).parent.absolute()
    patches_dir = os.path.join(script_dir, "patches")

    npm_path = shutil.which("npm")
    if not npm_path:
        print("Error: 'npm' not found on PATH. Install Node.js and ensure 'npm' is on your PATH.")
        return None

    if framework == "React":
        subprocess.run([npm_path, "create", "vite@latest", project_name, "--", "--template", "react"], check=True)
        os.chdir(project_name)
    elif framework == "Vue":
        subprocess.run([npm_path, "create", "vite@latest", project_name, "--", "--template", "vue"], check=True)
        os.chdir(project_name)
    elif framework == "Svelte":
        subprocess.run([npm_path, "create", "vite@latest", project_name, "--", "--template", "svelte"], check=True)
        os.chdir(project_name)
    else:
        print("Please initialize your project manually.")
        return None
    subprocess.run([npm_path, "install"], check=True)
    subprocess.run(["git", "init"], check=True)

    patch_path = os.path.join(patches_dir, framework.lower() + ".patch")
    subprocess.run(["git","apply", patch_path], check=True)
    os.chdir("..")
    return framework


def main():
    parser = argparse.ArgumentParser(

        description="Paneer CLI: Build and scaffold projects easily."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    build_parser = subparsers.add_parser("build", help="Build the application with PyInstaller")

    create_parser = subparsers.add_parser("create", help="Create a new frontend project")
    create_parser.add_argument("--framework", choices=["React", "Vue", "Svelte", "Other"], help="Framework to use")
    create_parser.add_argument("--project-name", help="Project name", default="my-app")

    run_parser = subparsers.add_parser("run", help="Run the application in development mode")

    args = parser.parse_args()

    if args.command == "build":
        try:
            npm_path = shutil.which("npm")
            if not npm_path:
                print("Error: 'npm' not found on PATH. Install Node.js and ensure 'npm' is on your PATH.")
                return
            subprocess.run([npm_path, "run", "build"], check=True)
        except subprocess.CalledProcessError:
            print("npm run build failed.")
            return

        os.makedirs("release", exist_ok=True)

        sep = ";" if os.name == "nt" else ":"

        # Include built frontend and paneer/libs DLLs
        add_data_args = [
            "--add-data", f"dist{sep}dist",
        ]
        try:
            paneer_root = resources.files("paneer")
            libs_path = paneer_root.joinpath("libs")

            libs_fs_path = str(libs_path)
            if os.path.isdir(libs_fs_path):
                add_data_args += ["--add-data", f"{libs_fs_path}{sep}paneer/libs"]
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
        ])
        print("Build complete.")
        return

    if args.command == "run":
        env = os.environ.copy()
        env['paneer_env'] = 'dev'
        procs = [
            subprocess.Popen([shutil.which("npm") or "npm", "run", "dev"], env=env),
            subprocess.Popen([sys.executable, "main.py"], env=env)
        ]
        for i in procs:
            i.wait()

        env['paneer_env'] = ''

    if args.command == "create":
        framework = args.framework
        project_name = args.project_name
        if framework is None:
            questions = [
                inquirer.List(
                    "framework",
                    message="Which frontend?",
                    choices=["React", "Vue", "Svelte", "Other"],
                ),
                inquirer.Text("project_name", message="Enter project name", default=project_name),
            ]
            answers = inquirer.prompt(questions) or {}
            framework = answers.get("framework")
            project_name = answers.get("project_name", project_name)

        if not framework:
            print("No framework selected.")
            return

        if framework != "Other":
            print(f"Using official {framework} scaffolder...")
            framework = run_scaffolder(framework, project_name)
            try:
                script_dir = pathlib.Path(__file__).parent.absolute()
                patches_dir = os.path.join(script_dir, "patches")
                os.chdir(project_name)
                shutil.copy(os.path.join(patches_dir, "example.py"), "main.py")
                os.chdir("..")
            except subprocess.CalledProcessError:
                print("Failed to connect to Github")
        else:
            print("Please initialize your project manually.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()