# Purpose
This tool is to help extract information from SonarQube server logs. For now it focuses on Compute Engine logs.

# Usage
- Checkout the project
- Simply call the python script:
```
python sonar_logs.py --help
```
- It's not rare that Python 3 binary is `python3` instead of `python`.
- Refer to the script help to provide needed arguments

# Use case
The script has different commands for different output:
- `tasks`: to export background tasks in a CSV file. It is much better to manipulate these data in a sheet to sort, filter, plot, search, etc.
- `steps`: to export all steps of all background tasks. The idea is the same than above but with a deeper granularity on tasks steps
- `report`: to compute some statistics about background tasks and output them in a short report
