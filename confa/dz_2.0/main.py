import os
import subprocess
import argparse
import datetime
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Visualize git commit dependency graph.")
    parser.add_argument("--plantuml-path", required=True, help="Path to PlantUML jar file.")
    parser.add_argument("--repo-path", required=True, help="Path to the git repository.")
    parser.add_argument("--output-path", required=True, help="Path to save the dependency graph image (PNG format).")
    parser.add_argument("--before-date", required=True, help="Include only commits before this date (YYYY-MM-DD).")
    return parser.parse_args()

def validate_paths(plantuml_path, repo_path, output_path):
    if not Path(plantuml_path).is_file():
        raise FileNotFoundError(f"PlantUML path '{plantuml_path}' does not exist or is not a file.")
    if not Path(repo_path).is_dir():
        raise NotADirectoryError(f"Repository path '{repo_path}' does not exist or is not a directory.")
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        os.makedirs(output_dir)

def fetch_commit_data(repo_path, before_date):
    os.chdir(repo_path)
    command = ["git", "log", f"--before={before_date}", "--pretty=format:%H|%P|%an|%ad", "--date=iso"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout.splitlines()

def parse_commit_data(commit_lines):
    commits = {}
    for line in commit_lines:
        hash_, parents, author, date = line.split('|')
        commits[hash_] = {
            "parents": parents.split() if parents else [],
            "author": author,
            "date": date
        }
    return commits

def generate_plantuml(commits):
    lines = ["@startuml"]  # Начало диаграммы
    for hash_, details in commits.items():
        label = f"{details['date']}\\n{details['author']}"
        lines.append(f"  {hash_} : {label}")  # Узел с меткой
        for parent in details["parents"]:
            lines.append(f"  {parent} --> {hash_}")  # Стрелка из родителя в текущий коммит
    lines.append("@enduml")  # Конец диаграммы
    return "\n".join(lines)



def create_graph_image(plantuml_text, plantuml_path, output_path):
    temp_puml_file = f"{output_path}.puml"
    with open(temp_puml_file, "w") as file:
        file.write(plantuml_text)

    try:
        subprocess.run(["java", "-jar", plantuml_path, temp_puml_file, "-o", str(Path(output_path).parent)], check=True)
    finally:
        if Path(temp_puml_file).exists():
            os.remove(temp_puml_file)

def main():
    args = parse_args()
    validate_paths(args.plantuml_path, args.repo_path, args.output_path)

    try:
        datetime.datetime.strptime(args.before_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    commit_lines = fetch_commit_data(args.repo_path, args.before_date)
    commits = parse_commit_data(commit_lines)
    plantuml_text = generate_plantuml(commits)
    create_graph_image(plantuml_text, args.plantuml_path, args.output_path)

    print(f"Dependency graph successfully saved to {args.output_path}.")

if __name__ == "__main__":
    main()