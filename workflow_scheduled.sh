#!/bin/bash
cd /c/Users/ethor/python-docs/draft-kings/draft-kings-db
micromamba activate draft-kings-db
echo $(date) >> logs/scheduled_task_stdout.log
echo $(date) >> logs/scheduled_task_stderr.log
./workflow.sh > >(tee -a logs/scheduled_task_stdout.log) 2> >(tee -a logs/scheduled_task_stderr.log)