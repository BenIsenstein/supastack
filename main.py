from enum import auto, StrEnum
import getpass
import os
import re
import subprocess

import inquirer

from subprocess_helper import run_command, run_command_with_retry


APP_NAME = "app_name"
PRIVACY = "privacy"
PROJECT_FOLDER = "project_folder"
PROJECT_REGION = "ca-central-1"
SUPABASE_ORG = "supabase_org"
SUPABASE_PSWD = "supabase_pswd"
SUPABASE_PLAN = "supabase_plan"


class Message(StrEnum):
    APP_NAME = "Enter Your Project Name"
    PRIVACY = "Would you like your new Github repo to be public or private?"
    PROJECT_FOLDER = "Select folder to install your project."
    SUPABASE_ORG = "Please paste your supabase organization ID?"
    SUPABASE_PSWD = "Please paste a db password for supabase?"
    SUPABASE_PLAN = "Which supabase plan are you on?"


class RepoPrivacy(StrEnum):
    PRIVATE = auto()
    PUBLIC = auto()


class SupabasePlan(StrEnum):
    FREE = auto()
    PRO = auto()


def validate_non_empty(answers, current):
    return current != ""


def main():
    questions = [
        inquirer.Text(APP_NAME, Message.APP_NAME, validate=validate_non_empty),
        inquirer.Path(
            PROJECT_FOLDER,
            message=Message.PROJECT_FOLDER,
            path_type=inquirer.Path.DIRECTORY,
            exists=True,
            default=".",
            validate=validate_non_empty,
            normalize_to_absolute_path=True,
        ),
        inquirer.List(PRIVACY, Message.PRIVACY, list(RepoPrivacy), RepoPrivacy.PUBLIC),
        inquirer.Text(SUPABASE_ORG, Message.SUPABASE_ORG, validate=validate_non_empty),
        inquirer.Password(
            SUPABASE_PSWD, message=Message.SUPABASE_PSWD, validate=validate_non_empty
        ),
        inquirer.List(
            SUPABASE_PLAN, Message.SUPABASE_PLAN, list(SupabasePlan), SupabasePlan.FREE
        ),
    ]

    responses = inquirer.prompt(questions)
    app_name = responses[APP_NAME]
    privacy = responses[PRIVACY]
    supabase_org = responses[SUPABASE_ORG]
    supabase_pswd = responses[SUPABASE_PSWD]
    supabase_plan = responses[SUPABASE_PLAN]

    run_command(f'cp -r -v react_template "{app_name}"')

    os.chdir(app_name)

    run_command("git init && git add . && git commit -m 'feat: create repo'")
    run_command(
        f"gh repo create '{app_name}' --{privacy} --source . --description 'Web app created with Supastack' --push"
    )
    run_command("git remote get-url origin")

    supabase_project_output, stderr = run_command(
        f'supabase projects create "{app_name}"  --db-password {supabase_pswd} --org-id {supabase_org} --plan {supabase_plan} --region {PROJECT_REGION}',
        stdout=subprocess.PIPE,
    )

    supabase_project_id = supabase_project_output.split("/")[-1].strip()

    print(supabase_project_output)

    supabase_keys_output, stderr = run_command_with_retry(
        f"supabase projects api-keys --project-ref {supabase_project_id}",
        stdout=subprocess.PIPE,
    )

    key = re.search(
        r"([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)", supabase_keys_output
    )
    start, end = key.span()
    supabase_anon_key = supabase_keys_output[start:end]

    os.chdir("terraform")

    with open("terraform.tfvars", "w+") as file:
        file.write(f'project_name = "{app_name}"\n')
        file.write(f'repo_name = "{app_name}"\n')
        file.write(f'supabase_key = "{supabase_anon_key}"\n')
        file.write(f'supabase_url = "https://{supabase_project_id}.supabase.co"')

    run_command(f"terraform init && terraform apply")
    run_command(f"git add . && git commit -m 'chore: commit tfstate' && git push")


if __name__ == "__main__":
    main()
