import os

import click
import git
import google.generativeai as genai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gemini_api_key = os.getenv("GOOGLE_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--model",
    default="gemini-2.5-pro",
    help="AI model to use for generating commit messages. Options: gemini-2.5-pro, gpt-4.1-mini",
)
def generate(model):
    """Generates a conventional commit message."""
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        click.echo("This is not a Git repository.")
        return

    staged_diffs = repo.index.diff("HEAD", create_patch=True)
    if not staged_diffs:
        click.echo("No staged files to commit.")
        return

    diffs = "".join(diff.diff.decode("utf-8") for diff in staged_diffs)
    commit_message = generate_commit_message(diffs, model)
    click.echo(commit_message)


def generate_commit_message(diffs, model):
    """Generates a commit message using the specified AI model."""
    prompt = f"""Generate a conventional commit message based on the code changes below.

RULES:
1. Use format: <type>(<scope>): <subject>
2. Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
3. Keep it simple - most commits should be one line
4. Focus on WHY the change was made, not WHAT files changed
5. Use imperative mood ("add" not "added")
6. Subject line ≤ 72 characters
7. Only add body/footer if the change is complex or breaking

EXAMPLES:
- feat(auth): add user login validation
- fix(api): handle null response in user fetch
- docs: update installation instructions
- refactor(parser): simplify token extraction logic

Look at this diff and write a clear, concise commit message:

{diffs}

Output only the commit message, no explanations."""

    try:
        if model == "gemini-2.5-pro":
            if not gemini_api_key:
                click.echo("Error: GOOGLE_API_KEY environment variable not set.")
                return None

            gemini_model = genai.GenerativeModel("gemini-2.5-pro")
            response = gemini_model.generate_content(prompt)
            return response.text

        elif model == "gpt-4.1-mini":
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

        else:
            click.echo(
                f"Error: Unsupported model '{model}'. Use 'gemini-2.5-pro' or 'gpt-4.1-mini'."
            )
            return None

    except Exception as e:
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
