#!/bin/bash -l
for d in 34-2014 02-2015
do
    for k in 1 2 3
    do
	for ep in 0 .25 .50 .75 1 1.25 1.5 1.75 2
	do
	    for name in gd #gd_neighborhood
	    do
		sbatch -o c_${d}_${k}_${ep}_${name}.out -e c_${d}_${k}_${ep}_${name}.err label_graph.sh ${d} ${k} ${ep}_${k} ${ep} ${name}
	    done
	done
    done
done
