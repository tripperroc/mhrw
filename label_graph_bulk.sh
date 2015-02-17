#!/bin/bash -l
for date in 02-2015 # X32015
do
    for deg in 0 1 1.75 2 2.25
    do
	for init in 1 2 3 4
	do
	    sbatch -o ${date}_D-${deg}_I-${init}.out -e ${date}_D-${deg}_I-${init}.err label_graph.sh ${date} ${deg} ${init}
			#./label_graph.sh ${d} ${k} ${ep}_${k} ${ep} ${name} ${init} ${prop} > c_${d}_${k}_${ep}_${name}_${init}_${prop}.out
	done
    done
done
