#!/bin/bash -l
for d in 34-2014 02-2015
do
    for k in 1 2 3
    do
	for ep in 0 .25 .50 .75 1 1.25 1.5 1.75 2
	do
	    for name in gd #gd_neighborhood
	    do
		output=`tail -1 c_${d}_${k}_${ep}_${name}.out`
		echo "time=${d} k=${k} ep=${ep} ${name}: ${output}"
	    done
	done
    done
done
