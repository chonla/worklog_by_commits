from datetime import time
from string import Template
import time
import yaml
import requests
import base64
import json
import re
from git import Repo

jira_items = {}

def first_line_of(commit_message):
    lines = commit_message.split("\n")
    return lines[0]

def transform_commit(commit_data):
    return {
        'comparable_date': time.strftime('%Y-%m-%d', time.localtime(commit_data['commit'].committed_date)),
        'date': time.strftime('%d %b %Y', time.localtime(commit_data['commit'].committed_date)),
        'project_name': commit_data['project'],
        'hash': str(commit_data['commit'].hexsha),
        'short_hash': str(commit_data['commit'].hexsha)[0:7],
        'message_1_line': first_line_of(commit_data['commit'].summary),
        'message': commit_data['commit'].summary,
        'jira_title': ''
    }

def print_commit(template, commit_data):
    tmpl = Template(template)
    print(tmpl.substitute(**commit_data))

def get_jira_id(commit_message):
    m = re.match(r"^([A-Za-z0-9]+\-\d+)\.", commit_message)
    if m is None:
        return None
    jira_id = m.group(1)
    return jira_id

def get_jira_item_info(team, id, username, password):
    if jira_id not in jira_items:
        url = "https://{team}.atlassian.net/rest/api/latest/issue/{id}".format(id=id, team=team)

        auth = base64.b64encode('{u}:{p}'.format(u=username,p=password).encode('ascii')).decode('ascii')
        req = requests.Request('GET', url, headers={'Authorization':'Basic {auth}'.format(auth=auth)})
        prepared = req.prepare()

        sess =requests.Session()
        res = sess.send(prepared)

        data = json.loads(res.content)

        if 'fields' in data:
            jira_items[id] = data["fields"]["summary"]
        else:
            jira_items[id] = None

    return jira_items[id]

if __name__ == "__main__":
    all_commits = {}
    worklog = {}
    with open("./log.yml", "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.CLoader)
        projects = data['projects']
        message_template = data['message']
        username = data['jira']['username']
        password = data['jira']['token']
        team = data['jira']['team']

        for project in projects:
            project_name = project['name']
            repo = Repo(project['path'])
            for branch in repo.branches:
                authors = data['criteria']['authors']
                for author in authors:
                    commits_in_branch = list(repo.iter_commits(branch, since=data["criteria"]["since"], until=data["criteria"]["until"], author=author))
                    for commit in commits_in_branch:
                        hash = str(commit.hexsha)
                        all_commits[hash] = { 'project': project_name, 'commit': commit}

        commits = all_commits.values()
        commits = sorted(commits, key=lambda data: data['commit'].committed_date, reverse=data['reverse'])

        distinct_commits_by_date = {}
        for commit in commits:
            commit_info = transform_commit(commit)
            jira_id = get_jira_id(commit_info['message_1_line'])
            if jira_id is not None:
                jira_title = get_jira_item_info(team, jira_id, username, password)
                if jira_title is None:
                    commit_info['jira_title'] = commit_info['message_1_line']
                else:
                    commit_info['jira_title'] = "{id}. {msg}".format(id=jira_id,msg=jira_title)
            else:
                commit_info['jira_title'] = commit_info['message_1_line']

            if commit_info['comparable_date'] not in distinct_commits_by_date:
                distinct_commits_by_date[commit_info['comparable_date']] = {"jira_ids":[],"commits":[]}

            if jira_id is None:
                distinct_commits_by_date[commit_info['comparable_date']]['commits'].append(commit_info)
            elif jira_id not in set(distinct_commits_by_date[commit_info['comparable_date']]['jira_ids']):
                distinct_commits_by_date[commit_info['comparable_date']]['jira_ids'].append(jira_id)
                distinct_commits_by_date[commit_info['comparable_date']]['commits'].append(commit_info)

        dates = sorted(distinct_commits_by_date.keys())
        for commited_date in dates:
            for jira_entry in distinct_commits_by_date[commited_date]['commits']:
                print_commit(message_template, jira_entry)