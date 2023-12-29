import subprocess
import sys
import os
import re

app_name = input('Project name: ')

os.chdir(f'{app_name}/terraform')

config_values = {}

with open('terraform.tfvars', 'r') as file:
    for line in file:
        key, value = map(str.strip, line.split('='))
        value = value.strip('"')
        config_values[key] = value

supabase_url = config_values.get('supabase_url')
supabase_id = re.search(r'https://([a-zA-Z0-9_-]+)\.supabase\.co', supabase_url).groups()[0]

with open('terraform.tfvars', 'a') as file:
    file.write('\nforce_destroy = true')

process = subprocess.Popen(
    "terraform apply && terraform destroy",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

os.chdir('../..')

process = subprocess.Popen(
    f"supabase projects delete {supabase_id}",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

process = subprocess.Popen(
    f"gh repo delete '{app_name}' --yes",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

process = subprocess.Popen(
    f"rm -rf '{app_name}'",
    text=True,
    shell=True
)

process.wait()

if process.returncode != 0:
    sys.exit(process.returncode)

