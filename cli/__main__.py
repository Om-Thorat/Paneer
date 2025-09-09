import inquirer
import subprocess
import os
import pathlib
import sys

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
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "create":
        questions = [
            inquirer.List(
                "framework",
                message="Which frontend?",
                choices=["React", "Vue", "Svelte", "Other"],
            ),
            inquirer.Text("project_name", message="Enter project name", default="my-app"),
        ]
        answers = inquirer.prompt(questions)
        framework = answers["framework"]
        project_name = answers["project_name"]

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