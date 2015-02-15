#!/bin/bash -l
for fname in `ls *.prop`
#for fname in `ls c_*.out`
do
	output=`tail -1 ${fname}`
	echo "${fname}: ${output}"
done
