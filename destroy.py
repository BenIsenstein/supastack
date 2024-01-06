import os
import re
from subprocess_helper import run_command

def main():
    app_name = input('Project name: ')
    config_values = {}

    os.chdir(f'{app_name}/terraform')

    with open('terraform.tfvars', 'r') as file:
        for line in file:
            key, value = map(str.strip, line.split('='))
            config_values[key] = value.strip('"')

    with open('terraform.tfvars', 'a') as file:
        file.write('\nforce_destroy = true')
    
    supabase_id = re.search(r'https://([a-zA-Z0-9_-]+)\.supabase\.co', config_values.get('supabase_url')).groups()[0]
    
    run_command("terraform apply && terraform destroy")

    os.chdir('../..')

    run_command(f"supabase projects delete {supabase_id}")
    run_command(f"gh repo delete '{app_name}' --yes")
    run_command(f"rm -rf '{app_name}'")

if __name__ == '__main__':
    main()
