#
#	Makefile for this SNAP example
#	- modify Makefile.ex when creating a new SNAP example
#
#	implements:
#		all (default), clean
#


include ../../Makefile.config
include Makefile.ex
include ../Makefile.exmain

#DATE=34-2014
#USER_LIST=../../../trowser3/34-2014_master_user_list.json
#TWITTER_GRAPH=../../../trowser3/34-2014_social_graph.json
MYPYTHONPATH=/home/choman/.local/lib/python2.6/site-packages
#LABEL=your_label
#K=k-fold-number
#EP=1

# This setting seemed to yield good results
# ./mhrw -file:gd_snap.graph -balance:.1 -flip:0 -num_swaps:10 -gayweight:1 -labweight:10 -greedy:0 -grad:100000

${DATE}_twitter_graph.${LABEL}.pkl: ${DATE}_master_user_list.json ${DATE}_social_graph.json
	python -OO generate_twitter_graph.py ${DATE}_master_user_list.json ${DATE}_social_graph.json ${DATE}_twitter_graph.${LABEL}.pkl

${DATE}_twitter_neighborhood_graph.${LABEL}.pkl: orientation-${DATE}.txt ${DATE}_twitter_graph.pkl 
	python -OO generate_twitter_neighborhood_graph.py orientation-${DATE}.txt ${DATE}_twitter_graph.${LABEL}.pkl ${DATE}_twitter_neighborhood_graph.${LABEL}.pkl

${DATE}_gd_snap.${LABEL}.graph ${DATE}_labeled_twitter_graph.${LABEL}.pkl: orientation-${DATE}-train.${K}.txt  orientation-${DATE}-test.${K}.txt ${DATE}_twitter_graph.${LABEL}.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.${K}.txt orientation-${DATE}-test.${K}.txt ${DATE}_twitter_graph.${LABEL}.pkl ${DATE}_gd_snap.${LABEL}.graph 1 ${DATE}_labeled_twitter_graph.${LABEL}.pkl ${DATE}_twitter_snap_translations.${LABEL}.pkl
	touch ${DATE}_gd_snap.${LABEL}.graph ${DATE}_labeled_twitter_graph.${LABEL}.pkl

${DATE}_gd_neighborhood_snap.${LABEL}.graph  ${DATE}_labeled_neighborhood_graph.${LABEL}.pkl: orientation-${DATE}-train.${K}.txt  orientation-${DATE}-test.${K}.txt ${DATE}_twitter_neighborhood_graph.${LABEL}.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.${K}.txt orientation-${DATE}-test.${K}.txt ${DATE}_twitter_neighborhood_graph.${LABEL}.pkl ${DATE}_gd_neighborhood_snap.${LABEL}.graph 1 ${DATE}_labeled_neighborhood_graph.${LABEL}.pkl ${DATE}_twitter_snap_neighborhood_translations.${LABEL}.pkl
	touch ${DATE}_gd_neighborhood_snap.${LABEL}.graph  ${DATE}_labeled_neighborhood_graph.${LABEL}.pkl

orientation-${DATE}.txt:
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; export PYTHONIOENCODING=utf-8; python twaydar.py ${DATE}_master_user_list.json > orientation-${DATE}.txt

${DATE}_twitter_clique_graph.${LABEL}.pkl: ${DATE}_labeled_twitter_graph.${LABEL}.pkl
	python -OO generate_max_clique_graph.py ${DATE}_labeled_twitter_graph.${LABEL}.pkl ${DATE}_twitter_clique_graph.${LABEL}.pkl

${DATE}_gd_clique_snap.graph: orientation-${DATE}-train.${K}.txt  orientation-${DATE}-test.${K}.txt ${DATE}_twitter_clique_graph.${LABEL}.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.${K}.txt orientation-${DATE}-test.${K}.txt ${DATE}_twitter_clique_graph.${LABEL}.pkl ${DATE}_gd_clique_snap.${LABEL}.graph ${EP} ${DATE}_labeled_twitter_clique_graph.${LABEL}.pkl ${DATE}_twitter_snap_clique_translations.${LABEL}.pkl

${DATE}_neighborhood_clique_graph.${LABEL}.pkl: ${DATE}_labeled_neighborhood_graph.${LABEL}.pkl
	python -OO generate_max_clique_graph.py ${DATE}_labeled_neighborhood_graph.${LABEL}.pkl ${DATE}_neighborhood_clique_graph.${LABEL}.pkl

${DATE}_gd_neighborhood_clique_snap.graph: orientation-${DATE}-train.${K}.txt  orientation-${DATE}-test.${K}.txt ${DATE}_neighborhood_clique_graph.${LABEL}.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.${K}.txt orientation-${DATE}-test.${K}.txt ${DATE}_neighborhood_clique_graph.${LABEL}.pkl ${DATE}_gd_neighborhood_clique_snap.${LABEL}.graph ${EP} ${DATE}_labeled_neighborhood_clique_graph.${LABEL}.pkl ${DATE}_neighborhood_Snap_clique_translations.${LABEL}.pkl
