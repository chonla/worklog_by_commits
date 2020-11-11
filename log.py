from datetime import time
from string import Template
import time
import yaml
from git import Repo

def first_line_of(commit_message):
    lines = commit_message.split("\n")
    return lines[0]

def transform_commit(commit_data):
    return {
        'date': time.strftime('%d-%b-%y', time.localtime(commit_data['commit'].committed_date)),
        'project_name': commit_data['project'],
        'hash': str(commit_data['commit'].hexsha),
        'short_hash': str(commit_data['commit'].hexsha)[0:7],
        'message_1_line': first_line_of(commit_data['commit'].summary),
        'message': commit_data['commit'].summary
    }

def print_commit(template, commit_data):
    tmpl = Template(template)
    print(tmpl.substitute(**transform_commit(commit_data)))

if __name__ == "__main__":
    all_commits = {}
    with open("./log.yml", "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.CLoader)
        projects = data['projects']
        message_template = data['message']

        for project in projects:
            project_name = project['name']
            repo = Repo(project['path'])
            for branch in repo.branches:
                commits_in_branch = list(repo.iter_commits(branch, since=data["criteria"]["since"], until=data["criteria"]["until"], author=data["criteria"]["author"]))
                for commit in commits_in_branch:
                    hash = str(commit.hexsha)
                    all_commits[hash] = { 'project': project_name, 'commit': commit}

        commits = all_commits.values()
        commits = sorted(commits, key=lambda data: data['commit'].committed_date, reverse=data['reverse'])

        for commit in commits:
            print_commit(message_template, commit)