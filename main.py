import subprocess

app_name = input('Project name: ')

command = "git clone https://github.com/BenIsenstein/open-data-react-supabase.git"

commands = command.split()
commands.append(f"'{app_name}'")

subprocess.Popen(
    commands,
    stderr=subprocess.STDOUT,
    stdout=subprocess.PIPE,
)
