#======================================================
# MLOPs Parsl Workflow
#======================================================
#
# This workflow simulates a typical MLOPs situation
# with the following tasks:
# 1. start an MLFlow tracking server
# 2. start DVC tracking within an architve repository + remote
# 3. download and preprocess training data
# 4. run training loop and store results on-the-fly with MLFlow
# 5. commit and push resulting models with DVC to repo + remote
# 6. use the model for inference and generate figures.
#
# Additional notebooks are provided for manually:
# 7. reusing the model for inference and generating figures
# 8. restart the MLFlow server to interactively browse the results.
#
# This workflow is supported by two Miniconda environments:
# 1. mlops-parsl - containing Parsl and it resides in the PW 
#    usercontainer and
# 2. mlops-apps - contains all the component applications 
#    (Parsl, TensorFlow, DVC, and MLFlow) of this workflow.
#
# This workflow uses only one Parsl Executor because
# multiple executors are not supported by Parsl monitoring.
# MLOPs could leverage multiple executors (i.e. CPU nodes
# running preprocessing followed by GPU nodes running
# training or inference) so that would make a nice
# extension to this workflow.
#======================================================
# Dependencies
#======================================================

# Basic dependencies
import os
from os.path import exists
from time import sleep

# Parsl essentials
import parsl
from parsl.app.app import python_app, bash_app
print(parsl.__version__, flush = True)

# PW essentials
import parsl_utils
from parsl_utils.config import config, resource_labels, form_inputs
from parsl_utils.data_provider import PWFile

#==================================================
# Step 1: Inputs
#==================================================

# Start assuming workflow is launched from the form.

# Gather inputs from the WORKFLOW FORM    
# The form_inputs, resource_labels, and
# Parsl config built by parsl_utils are
# all loaded above with the import statement.
# Each of these three data structures
# has different information:
# 1. resource_labels is a simple list of the 
#    resource names specified in the workflow
#    which are used for accessing more details
#    about each resource in the form_inputs or
#    Parsl config.
# 2. form_inputs is a record of the user selected
#    parameters of the workflow from the 
#    workflow.xml workflow launch form.  Additional
#    information is added by the PW platform. 
#    Some form information is *hidden* in the
#    workflow.xml and not visible to the user in
#    the GUI, but it can be modified by editing
#    the workflow.xml. This approach provides a
#    way to differentiate between commonly changed
#    parameters and parameters that rarely change.
# 3. the Parsl config is build by the PW platform
#    (specifically the parsl_utils wrapper used to
#    launch this workflow querying info from the
#    PW databases via the PW API). Some of this
#    information is duplicated in the form_inputs,
#    but it is in a special format needed by Parsl.
#
# Print out each of these data structures to see
# exactly what is contained in each.

print('--------------RESOURCE-LABELS---------------')
print(resource_labels)
print('----------------FORM-INPUTS-----------------')
print(form_inputs)
print('----------------PARSL-CONFIG----------------')
print(config)

# The main "scientific" workflow parameters (as opposed
# to all the params necessary to specify compute 
# resources, etc.) are in the geometry section of the
# workflow launch form.

# Initialize an empty string to append to.
params_run_str = ''

# Loop over each parameter in the geometry section.
for param in form_inputs['geometry']:
    print(param)
    params_run_str = params_run_str+param+";input;"+form_inputs['geometry'][param]+"|"

print(params_run_str)
# Write to params.run
with open("params.run","w") as f:
    n_char_written = f.write(params_run_str+"\n")

#==================================================
# Step 2: Configure Parsl
#==================================================
    
print("Loading Parsl config...")
parsl.load(config)
print("Parsl config loaded.")
    
#==================================================
# Step 3: Define Parsl workflow apps
#==================================================
    
# These apps are decorated with Parsl's `@bash_app` 
# and as such are executed in parallel on the compute 
# resources that are defined in the Parsl config 
# loaded above.  Functions that are **not** decorated 
# are not executed in parallel on remote resources. 
#
# The files that need to be staged to remote resources 
# will be marked with Parsl's `File()` (or its PW 
# extension, `PWFile()`) in the workflow.
    
print("Defining Parsl workflow apps...")

#===================================
# Launch MLFlow server
#===================================

# This decorator will print out the inputs and
# outputs (full local path, i.e. path where the
# parsl script is running) but is not strictly
# necessary for running the workflow.
@parsl_utils.parsl_wrappers.log_app
@bash_app(executors=[resource_labels[0]])
def start_mlflow(direct_input,inputs=[], outputs=[], stdout='mlflow.server.stdout', stderr='mlfow.server.stderr'):
        # The following lines between ''' are 
        # example bash commands that need to be
        # replaced with actual MLFlow server 
        # startup commands.
        return '''
        sleep 100
        hostname
        date
        whoami
        pwd
        ls
        echo {outdir}
        echo {srcdir}
        echo {runopt}
        '''.format(
            runopt = direct_input,
            srcdir = inputs[0].local_path,
            outdir = outputs[0].local_path
        )
    
#===================================
# App to download and preprocess data
#===================================
    
#===================================
# App to setup DVC tracking
#===================================

#===================================
# App to run training loop
#===================================

#===================================
# App to archive the ML results
#===================================

#===================================
# App to use the ML model for inference
#===================================

#==================================================
# Step 4: Workflow
#==================================================
 
# Get the local working directory. This should normally
# be /pw/jobs/<workflow_name>/<job_id>/
local_work_dir = os.getcwd()

# Set the remote working directory.
remote_work_dir = config.executors[0].working_dir+"/remote_work"
    
print("Starting MLFlow server...")
start_mlflow_future = start_mlflow(
    direct_input = "hello workflow",
    inputs = [
        PWFile(
            # Rsync with "copy dir by name" no trailing slash convention
            url = 'file://usercontainer/'+local_work_dir+'/test_input',
            local_path = remote_work_dir+'/test_input'
        )
    ],
    outputs = [
        PWFile(
            url = 'file://usercontainer/'+local_work_dir+'/outputs/test_output',
            local_path = remote_work_dir+'/test_output'
        )
    ],
    # Any files in outputs directory at end of app are rsynced back
    stdout = remote_work_dir+'/test_output/std.out',
    stderr = remote_work_dir+'/test_output/std.err'
)
    
# Force workflow to wait for app to finish
start_mlflow_future.result()
        
print('Done starting MLFlow.')

# Other apps go here.

print('Done with MLOPs workflow.')

