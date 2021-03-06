# mhrw
This repository contains code for preprocessing twitter data labeled
as straight or gay, and then run a Metropolis-Hastings random walk.
Requires:

* SNAP (snap.stanford.edu)
* Rochester twitter graph and user list
* Several python libraries, including networkx and pqdict.

This repo contains the necessary labeled data. To run, clone this repo
into the examples directory under snap. Then edit the Makefile with the
the location of any python libraries.

You need the following files.

* 02-2015_master_user_list.json
* 02-2015_social_graph.json

These are located, for instance, on

* cycle1.cs.rochester.edu

in

* /p/twitter4/rochester/02-2015

To build the larger neighborhood graph, type

>export DATE=02-2015; make ${DATE}_twitter_graph.pkl

To build the input to the MHRW, type

> export DATE=02-2015; make ${DATE}_gaydar_snap.graph

To compile the mhrw, type

> make

Here is an example of running the mhrw.

> ./mhrw -file:gaydar_snap.graph -balance:.5 -flip:0 -num_swaps:100 -grad:2500 -gayweight:10 -labweight:10 -greedy:0

The arguments are explained in mhrw.cpp
