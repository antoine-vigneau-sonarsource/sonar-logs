import argparse

def command_parsing():
    # Main parser (for common args)
    parser = argparse.ArgumentParser(description = 'SonarQube ComputeEngine logs processor')
    parser.add_argument('-i', '--input', required = True, help = 'Either one single file path, or a comma-separated list of directories with ce.*.log can be found (typically one or several SonarQube logs folders).')
    parser.add_argument('-o', '--output', required = True, help = 'Output file path.')
    parser.add_argument('-v', '--verbose', action = 'store_true')

    # Subparsers to split the main program by commands (taskscsv, stepscsv, report)
    subparsers = parser.add_subparsers(help = '', dest = 'command')
    subparsers.add_parser('tasks', help = 'Generate a CSV file of all background tasks')
    subparsers.add_parser('steps', help = 'Generate a CSV file of all steps of all background tasks')
    parser_report = subparsers.add_parser('report', help = 'Generate a summary and statistics about background tasks')
    parser_report.add_argument('-t', '--threshold', default = 80, type = int, help = 'Percentage of time spent by a step to be considered too long (relative to its background task). Default to 80%.')

    # Command parsing
    args = parser.parse_args()
    return args