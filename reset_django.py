import os
import subprocess
import sys

def run_command(command):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error: {command} failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    print("Installing required Python packages...")
    run_command("pip install -r requirements.txt")

    print("Removing old migration files...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and "migrations" in root and file != "__init__.py":
                os.remove(os.path.join(root, file))
            if file.endswith(".pyc") and "migrations" in root:
                os.remove(os.path.join(root, file))

    print("Removing SQLite database...")
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")

    print("Reinstalling Django...")
    run_command("pip uninstall -y django")
    run_command("pip install django")

    print("Creating new migrations...")
    run_command("python manage.py makemigrations")

    print("Applying migrations...")
    run_command("python manage.py migrate")

    print("Done! Your Django project has been reset.")

if __name__ == "__main__":
    main()