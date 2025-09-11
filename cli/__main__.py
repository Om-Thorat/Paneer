import inquirer
import subprocess
import os
import pathlib
import sys
import argparse
import PyInstaller.__main__

def run_scaffolder(framework, project_name):

    script_dir = pathlib.Path(__file__).parent.absolute()
    patches_dir = os.path.join(script_dir, "patches")

    if framework == "React":
        subprocess.run(["npm", "create", "vite@latest", project_name, "--", "--template", "react"], check=True)
        os.chdir(project_name)
    elif framework == "Vue":
        subprocess.run(["npm", "create", "vite@latest", project_name, "--", "--template", "vue"], check=True)
        os.chdir(project_name)
    elif framework == "Svelte":
        subprocess.run(["npm", "create", "vite@latest", project_name, "--", "--template", "svelte"], check=True)
        os.chdir(project_name)
    else:
        print("Please initialize your project manually.")
        return None
    subprocess.run(["npm", "install"], check=True)
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

    args = parser.parse_args()

    if args.command == "build":
        try:
            subprocess.run(["npm", "run", "build"], check=True)
        except subprocess.CalledProcessError:
            print("npm run build failed.")
            return

        os.makedirs("release", exist_ok=True)
        PyInstaller.__main__.run([
            "--collect-all", "paneer",
            "main.py",
            "--add-data", "dist/:dist,",
            "--distpath", "release",
        ])
        print("Build complete.")
        return

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
                subprocess.run(["cp", os.path.join(patches_dir, "example.py"), "main.py"], check=True)
                os.chdir("..")
            except subprocess.CalledProcessError:
                print("Failed to connect to Github")
        else:
            print("Please initialize your project manually.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()