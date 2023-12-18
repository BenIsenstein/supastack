import subprocess
import sys
import os
import getpass
import re
import time

app_name = input('Project name: ')
public_or_private = input('Would you like your new Github repo to be public or private? Type either "public" or "private". ')

process = subprocess.Popen(
    f'cp -r -v react_template "{app_name}"',
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

os.chdir(app_name)

process = subprocess.Popen(
    f"git init && git add . && git commit -m 'feat: create repo'",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

process = subprocess.Popen(
    f"gh repo create '{app_name}' --{public_or_private} --source . --description 'Web app created with Supastack' --push",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

process = subprocess.Popen(
    'git remote get-url origin',
    shell=True,
    text=True,
    stdout=subprocess.PIPE
)

repo_url, stderr = process.communicate()

if process.returncode != 0:
    sys.exit(process.returncode)

supabase_org = input('Please paste your supabase organization ID. ')
supabase_pswd = getpass.getpass('Please paste a db password for supabase. ')
supabase_plan = input('Which supabase plan are you on? Type "free" or "pro". (free) ') or 'free'

process = subprocess.Popen(
    f'supabase projects create "{app_name}"  --db-password {supabase_pswd} --org-id {supabase_org} --plan {supabase_plan} --region ca-central-1',
    shell=True,
    text=True,
    stdout=subprocess.PIPE
)

supabase_project_output, stderr = process.communicate()

if process.returncode != 0:
    sys.exit(process.returncode)

supabase_project_url = supabase_project_output.split()[-1].strip()
supabase_project_id = supabase_project_output.split('/')[-1].strip()

try_count = 0

while True:
    time.sleep(try_count * 2)

    process = subprocess.Popen(
        f'supabase projects api-keys --project-ref {supabase_project_id}',
        shell=True,
        text=True,
        stdout=subprocess.PIPE
    )

    supabase_keys_output, stderr = process.communicate()

    if process.returncode != 0:
        if try_count > 10:
            sys.exit(process.returncode)
        else:
            try_count += 1
            continue
    break
        
key = re.search(r'([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)', supabase_keys_output)
start, end = key.span()
supabase_anon_key = supabase_keys_output[start:end]

print(f"Created supabase project at {supabase_project_url}")

os.chdir('terraform')

with open('terraform.tfvars', 'w+') as file:
    file.write(f'project_name = "{app_name}"\n')
    file.write(f'repo_name = "{app_name}"\n')
    file.write(f'supabase_key = "{supabase_anon_key}"\n')
    file.write(f'supabase_url = "https://{supabase_project_id}.supabase.co"')

process = subprocess.Popen(
    f"terraform init && terraform apply",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

process = subprocess.Popen(
    f"git add . && git commit -m 'chore: commit tfstate' && git push",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

