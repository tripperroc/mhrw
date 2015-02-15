#!/bin/bash -l
for fname in `ls c_*.out`
do
	output=`tail -2 ${fname} | head -1`
	echo "${fname}: ${output}"
done
