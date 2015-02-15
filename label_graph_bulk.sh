#!/bin/bash -l
for d in 34-2014 02-2015 # X32015
do
    for k in 1 #2 3
    do
	for ep in 1.75 2.25
	do
	    for name in gd
            do
		for init in 1 2
		do
		    #for prop in 0 1
                    #do
			#sbatch -o c_${d}_${k}_${ep}_${name}_${init}_${prop}.out -e c_${d}_${k}_${ep}_${name}_${init}_${prop}.err label_graph.sh ${d} ${k} ${ep}_${k} ${ep} ${name} ${init} ${prop}
			./label_graph.sh ${d} ${k} ${ep}_${k} ${ep} ${name} ${init} ${prop} > c_${d}_${k}_${ep}_${name}_${init}_${prop}.out
                    #done
                 done
	    done
	done
    done
done
