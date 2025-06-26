import os

import click
import git
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@click.group()
def cli():
    pass


@cli.command()
def generate():
    """Generates a conventional commit message."""
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        click.echo("This is not a Git repository.")
        return

    staged_files = [item.a_path for item in repo.index.diff("HEAD")]
    if not staged_files:
        click.echo("No staged files to commit.")
        return

    diffs = repo.git.diff(staged_files)
    project_structure = get_project_structure()

    commit_message = generate_commit_message(staged_files, diffs, project_structure)
    click.echo(commit_message)


def generate_commit_message(staged_files, diffs, project_structure):
    """Generates a commit message using OpenAI."""
    prompt = f"""
    Generate a conventional commit message for the following changes.

    **Staged Files:**
    {staged_files}

    **Diffs:**
    {diffs}

    **Project Structure:**
    {project_structure}

    The commit message should be in the format:
    <type>(<scope>): <subject>
    <BLANK LINE>
    <body>
    <BLANK LINE>
    <footer>
    """

    try:
        # response = client.responses.create(
        #     model="gpt-4.1-nano",
        # )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates conventional commit messages.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    except OpenAIError as e:
        click.echo(f"Error generating commit message: {e}")
        return None


def get_project_structure(path=".", indent=""):
    structure = ""
    for item in os.listdir(path):
        if item.startswith("."):
            continue
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            structure += f"{indent}{item}/\n"
            structure += get_project_structure(item_path, indent + "  ")
        else:
            structure += f"{indent}{item}\n"
    return structure


if __name__ == "__main__":
    cli()
