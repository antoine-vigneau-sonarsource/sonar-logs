import os
import sys
import csv
import logging
from datetime import date, datetime
import utils.cli as cli
import utils.io as io
import utils.log_parser as log_parser

args = cli.command_parsing()
if args.verbose == True:
    logging.basicConfig(
        format = '%(asctime)s %(levelname)-8s %(message)s',
        level = logging.DEBUG,
        datefmt = '%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(
        format = '%(asctime)s %(levelname)-8s %(message)s',
        level = os.environ.get('LOGLEVEL', 'INFO'),
        datefmt = '%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)
log.info('Processing the input argument to get the file list')
files = io.extract_file_list(args.input)

match args.command:
    case 'tasks':
        tasks = log_parser.process_log_files(files)

        log.info('Write CSV file {}'.format(args.output))
        with open (args.output, 'w') as f:
            writer = csv.writer(f)
            header = ['id', 'project', 'type', 'branch', 'branch_type', 'pull_request', 'status', 'submitter', 'time', 'start', 'end']
            writer.writerow(header)

            c = 0
            for task in tasks.values():
                try:
                    writer.writerow([task.id, task.project, task.type, task.branch, task.branch_type, task.pull_request, task.status, task.submitter, task.time, task.start, task.end])
                    c += 1
                    if c % 1000 == 0:
                        log.debug('{} / {} tasks written'.format(c, len(tasks)))
                except AttributeError as e:
                    log.error('Missing attribute for task {}: {}'.format(task.id, e))
                    sys.exit()

    case 'steps':
        tasks = log_parser.process_log_files(files, True)

        log.info('Write CSV file {}'.format(args.output))
        with open (args.output, 'w') as f:
            writer = csv.writer(f)
            header = ['task_id', 'project', 'step', 'status', 'time', 'time_percent']
            writer.writerow(header)

            c = 0
            for task in tasks.values():
                for step in task.steps:
                    time_percent = 0
                    if task.time > 0:
                        time_percent = step.time / task.time * 100
                    try:
                        if task.type != 'AUDIT_PURGE':
                            writer.writerow([step.task_id, task.project, step.name, step.status, step.time, float(f'{time_percent:.1f}')])
                    except AttributeError as e:
                        log.error('Missing attribute for task {} step {}: {}'.format(task.id, step.name, e))
                        sys.exit()
                c += 1
                if c % 1000 == 0:
                    log.debug('{} / {} tasks written'.format(c, len(tasks)))

    case 'report':
        tasks = log_parser.process_log_files(files, True)
        
        log.info('Prepare report data...')
        tasks_REPORT = 0
        tasks_APP_REFRESH = 0
        tasks_VIEW_REFRESH = 0
        tasks_ISSUE_SYNC = 0
        tasks_AUDIT_PURGE = 0

        count_REPORT_time = 0
        average_REPORT_time = 0

        log_start_time = datetime.now()
        log_end_time = datetime.strptime('2000.01.01 00:00:00', '%Y.%m.%d %H:%M:%S')

        # TODO: collect more than the longest task, a top-10 would be more useful
        top_longest = ''
        top_longest_time = 0
        
        long_steps = {}

        for task in tasks.values():
            if isinstance(task.start, date) and task.start < log_start_time:
                log_start_time = task.start
            if isinstance(task.end, date) and task.end > log_end_time:
                log_end_time = task.end
            match task.type:
                case 'REPORT':
                    try:
                        tasks_REPORT += 1
                        count_REPORT_time += task.time
                        # Get the longest task
                        if task.time > top_longest_time:
                            top_longest = task.id
                            top_longest_time = task.time
                    except TypeError as e:
                        log.error('Task {}, tried to add {} and {} - Error: {}'.format(task.id, count_REPORT_time, task.time, e))
                        sys.exit()
                    # Get long steps (no more than 100)
                    if len(long_steps) < 100:
                        try:
                            if int(task.time) > 0:
                                for step in task.steps:
                                    time_percent = step.time / task.time * 100
                                    if time_percent > int(args.threshold):
                                        long_steps[task.id] = step.name
                        except ValueError as e:
                            pass
                case 'APP_REFRESH':
                    tasks_APP_REFRESH += 1
                case 'VIEW_REFRESH':
                    tasks_VIEW_REFRESH += 1
                case 'ISSUE_SYNC':
                    tasks_ISSUE_SYNC += 1
                case 'AUDIT_PURGE':
                    tasks_AUDIT_PURGE += 1

        log.info('Write report file')
        with open (args.output, 'w') as f:
            f.write('Files processed:\n')
            for file in files:
                f.write('   {}\n'.format(file))
            f.write('\n')
            # TODO: implement time window (requires tasks start and end date)
            f.write('Time window\n')
            f.write('   From {}\n'.format(log_start_time))
            f.write('   To   {}\n'.format(log_end_time))
            f.write('\n')
            f.write('Background tasks\n')
            f.write('   REPORT: {}\n'.format(tasks_REPORT))
            f.write('   APP_REFRESH: {}\n'.format(tasks_APP_REFRESH))
            f.write('   VIEW_REFRESH: {}\n'.format(tasks_VIEW_REFRESH))
            f.write('   ISSUE_SYNC: {}\n'.format(tasks_ISSUE_SYNC))
            f.write('   AUDIT_PURGE: {}\n'.format(tasks_AUDIT_PURGE))
            f.write('\n')
            f.write('Statistics\n')
            if (tasks_REPORT > 0):
                f.write('   Average REPORT time: {}\n'.format(count_REPORT_time / tasks_REPORT))
                f.write('   Longest task: {}\n'.format(top_longest))
                f.write('   Too long steps (above {}% of the total task time, 100 item max):\n'.format(args.threshold))
                for step_id in long_steps.keys():
                    f.write('      {}: {}\n'.format(step_id, long_steps[step_id]))
                f.write('\n')
            else:
                f.write('   No report task\n')
        
