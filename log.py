from datetime import time
import time
import yaml
from git import Repo

def first_line_of(commit_message):
    lines = commit_message.split("\n")
    return lines[0]


def print_commit(project_name, commit):
    print("{time} [{project_name}] {msg} #{hash}".format(
        time = time.strftime('%Y-%m-%d', time.localtime(commit.committed_date)),
        project_name = project_name,
        hash = str(commit.hexsha)[0:7],
        msg = first_line_of(commit.summary)
        ))

if __name__ == "__main__":
    all_commits = {}
    with open("./log.yml", "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.CLoader)
        projects = data['projects']

        for project in projects:
            project_name = project['name']
            repo = Repo(project['path'])
            for branch in repo.branches:
                commits_in_branch = list(repo.iter_commits(branch, since=data["criteria"]["since"], until=data["criteria"]["until"], author=data["criteria"]["author"]))
                for commit in commits_in_branch:
                    hash = str(commit.hexsha)
                    all_commits[hash] = { 'project': project_name, 'commit': commit}

    commits = all_commits.values()
    commits = sorted(commits, key=lambda data: data['commit'].committed_date, reverse=True)

    for commit in commits:
        print_commit(commit['project'], commit['commit'])