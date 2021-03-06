# Worklog by commits

Create worklog by commit messages/JIRA title from several projects.

## Configuration Example (log.yml)

```yml
projects:
    - name: New Core System
      path: ../confidential-project/core
    - name: New Core UI
      path: ../confidential-project/ui
    - name: New Core Document
      path: ../confidential-project/docs
    - name: Experiments
      path: ../experiment
criteria:
    since: "2020-09-01"
    until: "2020-11-30"
    authors:
        - author1@emailaddress.com
        - author2@emailaddress.com
message: "${date}\tS1\t\t[${project_name}] ${message_1_line}"
reverse: false
jira:
    team: myteam
    username: author1@emailaddress.com
    token: dairCKAOjg02ncaSDF
```

## Variables

Variables can be used in message template.

| Variable Name | Description |
| ---- | ---- |
| date | Committed Date in 1-Jan-1970 format |
| project_name | Project name defined in yaml |
| hash | Commit ID |
| short_hash | Shortened commit ID |
| message_1_line | The first line of commit message |
| message | Commit message |
| jira_title | Jira item's title |

## Installation

```bash
pip3 install -r ./requirements.txt
```

## Print log

```bash
python3 ./log.py
```