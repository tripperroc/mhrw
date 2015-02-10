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
MYPYTHONPATH=/usr/local/lib/python2.7/site-packages/

# This setting seemed to yield good results
# ./mhrw -file:gaydar_snap.graph -balance:.1 -flip:0 -num_swaps:10 -gayweight:1 -labweight:10 -greedy:0 -grad:100000

${DATE}_twitter_graph.pkl: ${DATE}_master_user_list.json ${DATE}_social_graph.json
	python -OO generate_twitter_graph.py ${DATE}_master_user_list.json ${DATE}_social_graph.json ${DATE}_twitter_graph.pkl

${DATE}_twitter_neighborhood_graph.pkl: orientation-${DATE}.txt ${DATE}_twitter_graph.pkl 
	python -OO generate_twitter_neighborhood_graph.py orientation-${DATE}.txt ${DATE}_twitter_graph.pkl ${DATE}_twitter_neighborhood_graph.pkl

${DATE}_gaydar_snap.graph ${DATE}_labeled_twitter_graph.pkl: orientation-${DATE}-train.txt  orientation-${DATE}-test.txt ${DATE}_twitter_graph.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.txt orientation-${DATE}-test.txt ${DATE}_twitter_graph.pkl ${DATE}_gaydar_snap.graph 1 ${DATE}_labeled_twitter_graph.pkl ${DATE}_twitter_snap_translations.pkl
	touch ${DATE}_gaydar_snap.graph ${DATE}_labeled_twitter_graph.pkl

${DATE}_gaydar_neighborhood_snap.graph: orientation-${DATE}-train.txt  orientation-${DATE}-test.txt ${DATE}_twitter_neighborhood_graph.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.txt orientation-${DATE}-test.txt ${DATE}_twitter_neighborhood_graph.pkl ${DATE}_gaydar_neighborhood_snap.graph 1 ${DATE}_labeled_neighborhood_graph.pkl ${DATE}_twitter_snap_neighborhood_translations.pkl

orientation-${DATE}.txt:
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; export PYTHONIOENCODING=utf-8; python twaydar.py ${DATE}_master_user_list.json > orientation-${DATE}.txt

${DATE}_twitter_clique_graph.pkl: ${DATE}_labeled_twitter_graph.pkl
	python -OO generate_max_clique_graph.py ${DATE}_labeled_twitter_graph.pkl ${DATE}_twitter_clique_graph.pkl

${DATE}_gaydar_clique_snap.graph: orientation-${DATE}-train.txt  orientation-${DATE}-test.txt ${DATE}_twitter_clique_graph.pkl
	export PYTHONPATH=$PYTHONPATH:${MYPYTHONPATH}; python -OO write_snap3.py orientation-${DATE}-train.txt orientation-${DATE}-test.txt ${DATE}_twitter_clique_graph.pkl ${DATE}_gaydar_clique_snap.graph 1 ${DATE}_labeled_twitter_clique_graph.pkl ${DATE}_twitter_snap_clique_translations.pkl
