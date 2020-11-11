# Worklog by commits

Create worklog by commit messages from several projects.

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
    author: chonlasith@gmail.com
```

## Installation

```bash
pip3 install -r ./requirements.txt
```

## Print log

```bash
python3 ./log.py
```