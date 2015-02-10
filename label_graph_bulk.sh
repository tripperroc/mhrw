#!/bin/bash -l
for date in 34-2014 02-2015
do
    for k in 1 2 3
    do
	for ep in 0 .25 .50 .75 1 1.25 1.5 1.75 2
	do
	    for name in gd gd_neighborhood
	    do
		sbatch analyze.sh $date $k $ep_$k $ep $name
	    done
	done
    done
done
