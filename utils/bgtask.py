import sys
import re
import logging
from datetime import datetime

log = logging.getLogger(__name__)

class BGTask:
    def __init__(self, id = '', project = '', type = '', branch = '', branch_type = '', pull_request = '', status = '', submitter = '', time = 0, start = '', end = ''):
        self.id = id
        self.project = project
        self.type = type
        self.branch = branch
        self.branch_type = branch_type
        self.pull_request = pull_request
        self.status = status
        self.submitter = submitter
        self.time = time
        self.start = start
        self.end = end
        self.steps = []

    def __init__(self, input):
        self.id = ''
        self.project = ''
        self.type = ''
        self.branch = ''
        self.branch_type = ''
        self.pull_request = ''
        self.status = ''
        self.submitter = ''
        self.time = 0
        self.start = ''
        self.end = ''
        self.steps = []

        try:
            # The input is a log line
            if input.find('Execute task') > 0:
                attributes = {}
                items = input.split('|')
                for item in items:
                    if item.find('=') > 0:
                        t = item.split('=')
                        attributes[t[0]] = t[1]
                # Sort attributes in object fields
                for key in attributes.keys():
                    match key.strip():
                        case 'id':
                            self.id = attributes[key].strip()
                        case 'project':
                            self.project = attributes[key].strip()
                        case 'type':
                            self.type = attributes[key].strip()
                        case 'branch':
                            self.branch = attributes[key].strip()
                        case 'branchType':
                            self.branch_type = attributes[key].strip()
                        case 'pullRequest':
                            self.pull_request = attributes[key].strip()
                        case 'submitter':
                            self.submitter = attributes[key].strip()
                # Collect the start date (format is YYYY.MM.DD HH:MM:SS)
                self.start = datetime.strptime(input[0:19], '%Y.%m.%d %H:%M:%S')

            # The input is a task id
            else:
                self.id = input

        except IndexError as e:
            log.error('Index Error while handling the following input: {} (Error message: {})'.format(input, e))
            sys.exit()


class BGStep:
    def __init__(self, task_id, name, status, time):
        self.task_id = task_id
        self.name = name
        self.status = status
        self.time = time

    def __init__(self, line):
        try:
            items = line.split('|')
            # 0: Task ID and name
            # 1, 2, 3...: random fields including Status and Time
            self.task_id = re.search('ce\[([^\]]+)\]', items[0]).group(1)
            self.name = re.search('ComputationStepExecutor\]\s([^\|]+)$', items[0]).group(1).strip()
            for item in items[1:]:
                if (item.strip().startswith('status')):
                    status_items = item.split('=')
                    self.status = status_items[1].strip()
                elif (item.strip().startswith('time')):
                    self.time = int(re.search('time=([0-9]*)ms', item).group(1))
        except IndexError as e:
            log.error('Index Error while handling the following input: {} (Error message: {})'.format(input, e))
            sys.exit()


# Project analysis
# 2022.07.28 15:31:22 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=js | type=REPORT | id=AYJFbwwH21mhZjlHWBoC
# 2022.07.28 15:34:33 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=js | type=REPORT | branch=feature | branchType=BRANCH | id=AYJFcfYh21mhZjlHWBoR
# 2022.07.28 15:37:20 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=js | type=REPORT | pullRequest=1 | id=AYJFdIEQ21mhZjlHWBoW

# Application
# 2022.07.28 15:32:18 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=MyApplication | type=APP_REFRESH | id=AYJFb-eO21mhZjlHWBoF | submitter=admin
# 2022.07.28 15:33:51 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=MyApplication | type=APP_REFRESH | branch=develop | branchType=BRANCH | id=AYJFcU0J21mhZjlHWBoN | submitter=admin

# Portfolio
# 2022.07.28 15:33:07 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=MyPortfolio | type=VIEW_REFRESH | id=AYJFcKSw21mhZjlHWBoG | submitter=admin

# ISSUE_SYNC tasks
# 2022.07.28 15:27:08 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=MyApplication | type=ISSUE_SYNC | branch=master | branchType=BRANCH | id=AYJFawUl21mhZjlHWBmJ
# 2022.07.28 15:27:10 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | project=support-33244 | type=ISSUE_SYNC | branch=master | branchType=BRANCH | id=AYJFawUl21mhZjlHWBmK

# AuditPurge
# 2022.07.28 16:26:55 INFO  ce[][o.s.c.t.CeWorkerImpl] Execute task | type=AUDIT_PURGE | id=AYJFoehK21mhZjlHWBoY