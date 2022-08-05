import fileinput
import re
import logging
import utils.bgtask as bgtask

log = logging.getLogger(__name__)

def process_log_files(files, with_steps = False):
    log.info('Processing log files to extract tasks info')
    tasks = {}
    for file in files:
        log.debug('Processing log file {}'.format(file))
        for line in fileinput.input(file):
            if line.find('INFO') > 0:
                if line.find('Execute task') > 0:
                    task = bgtask.BGTask(line)
                    tasks[task.id] = task
                if line.find('Executed task') > 0:
                    task_id = re.search('ce\[([^\]]+)\]', line).group(1)
                    if task_id not in tasks:
                        tasks[task_id] = bgtask.BGTask(task_id)
                    time = int(re.search('time=([0-9]*)ms', line).group(1))
                    tasks[task_id].time = time
                    status = re.search('status=([^\s]*)', line).group(1)
                    tasks[task_id].status = status
                if with_steps and line.find('ComputationStepExecutor') > 0:
                    step = bgtask.BGStep(line)
                    if step.task_id not in tasks:
                        tasks[step.task_id] = bgtask.BGTask(step.task_id)
                    tasks[step.task_id].steps.append(step)
    return tasks