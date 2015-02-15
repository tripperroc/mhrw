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
#SBATCH --mem-per-cpu=10000


# Your job script goes below this line.
export DATE=$1; export K=$2; export LABEL=$3; export EP=$4; export INIT=$6; 
MYPYTHONPATH=/home/choman/.local/lib/python2.6/site-packages
export PYTHONPATH=${PYTHONPATH}:${MYPYTHONPATH}
python -OO write_snap${INIT}.py orientation-${DATE}-train.txt orientation-${DATE}-heldout.txt ${DATE}_twitter_graph.pkl ${DATE}_gd_snap.${LABEL}.${INIT}.graph ${EP} ${DATE}_labeled_twitter_graph.${LABEL}.${INIT}.pkl ${DATE}_twitter_snap_translations.${LABEL}.${INIT}.pkl
for p in 0 1
do
    for q in 0 1
    do
       export PROP=${p};
       #make ${DATE}_$5_snap.${LABEL}.${INIT}.${PROP}.prop
       #make ${DATE}_$5_snap.${LABEL}.${INIT}.graph
       #make ${DATE}_twitter_graph.pkl
       ./newty -file:${DATE}_gd_snap.${LABEL}.${INIT}.graph -discrete:${PROP} > ${DATE}_gd_snap.${LABEL}.${INIT}.${PROP}.prop
    done
done
