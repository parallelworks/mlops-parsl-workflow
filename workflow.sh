#!/bin/bash
set -x

# Execution transfers to here when the `Execute` button
# is pressed on the workflow launch form.

#----------------------------------------
# Set up Parsl integration tools
#----------------------------------------

# Grab current version of parsl_utils
# or specify branch with -b
git clone https://github.com/parallelworks/parsl_utils.git parsl_utils

# Set the version of workflow-utils which is 
# pulled and used by parsl_utils.
export workflow_utils_branch=main

#------------------------------------------
# Launch!
#------------------------------------------
# Cannot run scripts inside parsl_utils directly
bash parsl_utils/main.sh $@

#------------------------------------------
# What's next?
#------------------------------------------
# The parsl_utils/main.sh will gather information
# about the resources specified in the launch form
# (available in inputs.sh and inputs.json) and
# then launches the main.py in this workflow
# directory. Main.py is the main Parsl orchestration
# script.

