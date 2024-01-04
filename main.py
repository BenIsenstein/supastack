import subprocess
import os
import getpass
import re
from subprocess_helper import run_command, run_command_with_retry

def main():
    app_name = input('Project name: ')
    public_or_private = input('Would you like your new Github repo to be public or private? Type either "public" or "private". ')

    run_command(f'cp -r -v react_template "{app_name}"')

    os.chdir(app_name)

    run_command("git init && git add . && git commit -m 'feat: create repo'")
    run_command(f"gh repo create '{app_name}' --{public_or_private} --source . --description 'Web app created with Supastack' --push")

    supabase_org = input('Please paste your supabase organization ID. ')
    supabase_pswd = getpass.getpass('Please paste a db password for supabase. ')
    supabase_plan = input('Which supabase plan are you on? Type "free" or "pro". (free) ') or 'free'

    supabase_project_output, stderr = run_command(
        f'supabase projects create "{app_name}"  --db-password {supabase_pswd} --org-id {supabase_org} --plan {supabase_plan} --region ca-central-1',
        stdout=subprocess.PIPE
    )

    supabase_project_id = supabase_project_output.split('/')[-1].strip()

    print(supabase_project_output)

    supabase_keys_output, stderr = run_command_with_retry(
        f'supabase projects api-keys --project-ref {supabase_project_id}',
        stdout=subprocess.PIPE
    )

    key = re.search(r'([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)', supabase_keys_output)
    start, end = key.span()
    supabase_anon_key = supabase_keys_output[start:end]

    os.chdir('terraform')

    with open('terraform.tfvars', 'w+') as file:
        file.write(f'project_name = "{app_name}"\n')
        file.write(f'repo_name = "{app_name}"\n')
        file.write(f'supabase_key = "{supabase_anon_key}"\n')
        file.write(f'supabase_url = "https://{supabase_project_id}.supabase.co"')

    run_command(f"terraform init && terraform apply")
    run_command(f"git add . && git commit -m 'chore: commit tfstate' && git push")

if __name__ == '__main__':
    main()
