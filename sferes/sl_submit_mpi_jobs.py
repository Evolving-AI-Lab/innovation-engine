#!/usr/bin/python
import os, commands, sys

# -------- SETTINGS ------------
#projectGroup = "RIISVis"
projectGroup = "EvolvingAI"
numRuns = 1
runName = str(sys.argv[1]) # 1005
yourMail = "anguyen8@uwyo.edu"
runName = runName
numCores = 128  # A multiple of 16
numGPU = 0
numHours = 120 
startFrom = 90

pathCurrentDir = os.path.dirname(os.path.abspath(__file__)) # Path to current directory without trailing slash '/'
executable = pathCurrentDir + "/build/default/exp/images/images_"+ runName  +" "
# ---------------------------------

numNodes = str(numCores/16)
YourInputParameter1 = str(10)
#options = ""
#options = "--your_option your_value --your_second_option $your_variable --your_third_variable " + YourInputParameter1
options = "$seed_num "
scriptFileName = "launchScript.sh"


def printScriptFile():
    scriptFile  = open(scriptFileName,'w',)

    #This will print the header of the launch script
    scriptFile.write( "#!/bin/bash\n")
    scriptFile.write( "\n")
    scriptFile.write( "#Do not edit. File automatically generated\n")
    scriptFile.write( "\n")

    scriptFile.write( "#SBATCH --ntasks="+ str(numCores) + "\n" );
    scriptFile.write( "#SBATCH --nodes="+ str(numNodes) + "\n" );
    #scriptFile.write( "#SBATCH --ntasks-per-node=16 \n");   # Jared suggested not to use --ntasks, --nodes, and --ntasksper-node all together
    #scriptFile.write( "#SBATCH --cpus-per-task=1 \n");

    if numGPU > 0:
	scriptFile.write( "#SBATCH --gres=gpu:1    # GPU\n");
    
    #scriptFile.write( "#SBATCH -J "+ runName +"    # job name \n");
    scriptFile.write( "#SBATCH -A "+ projectGroup +" \n");
    #scriptFile.write( "#SBATCH -e LOG."+ runName +".err \n");
    #scriptFile.write( "#SBATCH -o LOG."+ runName +".log         # output and error file name (%j expands to jobID) \n");
    scriptFile.write( "#SBATCH -t "+ str(numHours) +":00:00        # run time (hh:mm:ss) - 48 hours \n");
    scriptFile.write( "#SBATCH --mail-user="+ yourMail  +" \n");
    scriptFile.write( "#SBATCH --mail-type=begin  # email me when the job starts \n");
    scriptFile.write( "#SBATCH --mail-type=end    # email me when the job finishes \n");

    #Write any modules, environment variables or other commands your program needs before it is being executed here
    #Always load compiler module first. See command "module spider" for available modules
    scriptFile.write( "module load gnu/4.8.3\n")
    #scriptFile.write( "module load cuda/6.5\n")
    scriptFile.write( "module load openmpi/1.8.4\n")

    log_dir = "/gscratch/EvolvingAI/anguyen8/log/$SLURM_JOBID"

    # Here we define the parameters sent to the program
    scriptFile.write( "seed_number=\"${1}\" \n")
    scriptFile.write( "experimentDir=\"${2}\" \n")
    scriptFile.write( "export OMPI_MCA_orte_tmpdir_base=%s \n" % log_dir)
    scriptFile.write( "export TEST_TMPDIR=%s \n" % log_dir )  # GLOG
    scriptFile.write( "export TMPDIR=%s \n" % log_dir )
    scriptFile.write( "export TMP=%s \n" % log_dir )
    scriptFile.write( "mkdir %s \n" % log_dir )


    #Here we change to the directory where the experiment will be executed
    #Note that experiment dir is a variable that is not defined here
    scriptFile.write( "echo \"Changing to directory: \" $experimentDir\n")
    scriptFile.write( "cd $experimentDir\n")
    scriptFile.write( "\n")

    #Echo what we will execute to a file called runToBe
    scriptFile.write( "echo \" " + executable + options + " > thisistheoutput 2> err.log\" > runToBe\n")

    #Actually execute your program
    #scriptFile.write( "time mpirun --mca mpi_leave_pinned 0 --mca mpi_warn_on_fork 0 -np " + str(numCores) + " " + executable + options + " > thisistheoutput 2> err.log\n")
    #scriptFile.write( "time srun " + executable + options + " > output.log 2> err.log\n")
    scriptFile.write( "srun " + executable + options + " > output.log 2> err.log\n")
    scriptFile.write( "rm -rf %s \n" % log_dir )

    #This will print the footer of the launch script
    scriptFile.write( "\n")
    scriptFile.write( "echo \"Done with run\"\n")
    scriptFile.close()

    #Here we make the launch script executable
    os.system("chmod +x " + scriptFileName)

################
# main starts here #
################

print 'Starting a batch of runs called: ' + runName

printScriptFile()

for i in range(startFrom, startFrom + numRuns):
    #Create a new directory for our run
    runNumStr = str(i)

    runDirShort = "run_" + runName + "_" + runNumStr
    #runDirShort = "run_" + runNumStr.zfill(numRuns/10)
    # If there is a path.. continue
    if os.path.isdir(runDirShort):
        print runDirShort + " already exists. Abort!"
        #sys.exit(3)
    else:	# Create a new run_x folder
        command = "mkdir "  + runDirShort
        os.system(command)

    pwd = commands.getoutput("pwd")
    experimentDir = pwd + "/" + runDirShort

    #Set your own variables
    seed_num = str(i) 

    #Create the command that will submit your experiment
    #command = ("sbatch --export=seed_num=" + variableThatShouldBeDifferentForEachRun
    command = ("sbatch"
               #+ ",experimentDir=" + experimentDir
               + " -o " + experimentDir + "/myOut"
               + " -e " + experimentDir + "/myErr"
               + " -J " + runName + "_" + runNumStr + " " + scriptFileName
               + " " + seed_num
               + " " + experimentDir )

    print command

    #Launch your experiment
    os.system(command)
