#!/bin/bash -l
# NOTE the -l flag!
#

# This is an example job file for a single core CPU bound program
# Note that all of the following statements below that begin
# with #SBATCH are actually commands to the SLURM scheduler.
# Please copy this file to your home directory and modify it
# to suit your needs.
# 
# If you need any help, please email rc-help@rit.edu
#

# Name of the job - You'll probably want to customize this.
#SBATCH -J label_graph

# Standard out and Standard Error output files

#To send emails, set the adcdress below and remove one of the "#" signs.  
#SBATCH --mail-user cmh@cs.rit.edu 
# notify on state change: BEGIN, END, FAIL or ALL #SBATCH --mail-type=ALL

# Request 5 minutes run time MAX, anything over will be KILLED
#SBATCH -t 12:0:0

# Put the job in the "debug" partition and request one core
# "debug" is a limited partition.  You'll likely want to change
# it to "work" once you understand how this all works.
#SBATCH -p standard
#SBATCH -n 1

# Job memory requirements in MB
#SBATCH --mem-per-cpu=100000


# Your job script goes below this line.
	  
export EP=$2; export INIT=$3; export DATE=$1
#MYPYTHONPATH=/home/choman/.local/lib/python2.6/site-packages
MYPYTHONPATH=/usr/local/lib/python2.7/site-packages/
export PYTHONPATH=${PYTHONPATH}:${MYPYTHONPATH}

python -OO urdata/write_age_snap${INIT}.py urdata/trainingData.txt urdata/testingData.txt urdata/twitter_age_graph.pkl urdata/${DATE}_D-${EP}_I-${INIT}.graph ${EP} urdata/${DATE}_labeled_twitter_graph_D-${EP}_I-${INIT}.pkl urdata/${DATE}_twitter_snap_trans_D-${EP}_I-${INIT}.pkl urdata/labeled_users_true.txt > urdata/02-2015_D-${EP}_I-${INIT}.init_results

./newty -file:urdata/${DATE}_D-${EP}_I-${INIT}.graph -discrete:1 > urdata/02-2015_D-${EP}_I-${INIT}_disc.iter_results

if [ "$INIT" == "3" ]
then
    ./newty -file:urdata/${DATE}_D-${EP}_I-${INIT}.graph -discrete:0 > urdata/02-2015_D-${deg}_I-${init}_cont.iter_results
fi

#python ./mhrw -file:${DATE}_D-${EP}_I-${INIT}.graph -swaps:1000 > 02-2015_D-${deg}_I-${init}_mhrw.iter_results
