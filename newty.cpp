#include <iostream>
#include <fstream>
#include <sstream>
#include <math.h>
//#include <time>
#include "Snap.h"



using namespace std;

//static TRnd my_random ((int) time(NULL));
static TRnd my_random (1);

class Model {

private:
  PUNGraph p;
  double * edge_weights;
  int numlabels;
  THash<TPair<TInt, TInt>, float> edgeweight;
  int numtestlabels;
  int discrete;
  
public:
  double * new_labels;
  double * labels;
  int * test_labels;
  double gay_fraction;
  double target_gay_fraction;
  
  
  Model (PUNGraph p, double * labels, double * new_labels, int numlabels, THash<TPair<TInt, TInt>, float> edgeweight, int numtestlabels, int * test_labels, int discrete): p(p), labels(labels), new_labels(new_labels), numlabels(numlabels), edgeweight(edgeweight), numtestlabels(numtestlabels), test_labels(test_labels), discrete(discrete) {
    edge_weights = new double[p->GetNodes()];   
    
    for (TUNGraph::TNodeI n = p->BegNI(); n != p->EndNI(); n++) {
      TInt ego = n.GetId();
      TInt neighborhood_size = n.GetDeg();
      
      double neighborhood_weight = 0;
      for (int i = 0; i < neighborhood_size; i++) {
	TInt alter = n.GetNbrNId(i);

	double neighbor_weight = edgeweight.GetDat(TPair<TInt, TInt>(min(ego,alter), max(ego,alter)));
	neighborhood_weight += neighbor_weight;

      }
      edge_weights[ego] = neighborhood_weight;
    }
  }

  ~Model () {
    // delete temp_labels;
  }
  /*
   * Calculates the log probability of a given label set
   */
  double tic  () {

    int gay_labeled_gay = 0,
      gay_labeled_straight = 0,
      gay_unlabeled = 0,
      straight_labeled_straight = 0,
      straight_labeled_gay = 0,
      straight_unlabeled = 0;
    
    double total_err = 0;
    
    for (TUNGraph::TNodeI n = p->BegNI(); n != p->EndNI(); n++) {
      
      TInt ego = n.GetId();
      
      if (ego >= numlabels) {
	new_labels[ego] = 0;
	TInt neighborhood_size = n.GetDeg();
	for (int i = 0; i < neighborhood_size; i++) {
	
	  TInt alter = n.GetNbrNId(i);
	  double neighbor_weight = edgeweight.GetDat(TPair<TInt, TInt>(min(ego,alter), max(ego,alter)));
	  new_labels[ego] += neighbor_weight * labels[alter]/edge_weights[ego];
	}
	if (discrete == 1) new_labels[ego] = new_labels[ego] > 0 ? 1 : -1;
	double duh = labels[ego]-new_labels[ego];
	duh = duh < 0 ? -duh : duh;
	total_err += duh;
	//cerr << ego << " " << numlabels << " " << numtestlabels << endl;
	if (ego < numlabels + numtestlabels ) {
	  TInt ego2 = ego - numlabels;
	  if (test_labels[ego2] > 0) {
	    if (labels[ego] > 0) gay_labeled_gay++;
	    else if (labels[ego] < 0) gay_labeled_straight++;
	    else gay_unlabeled++;
	  }
	  if (test_labels[ego2] < 0) {
	    if (labels[ego] > 0) straight_labeled_gay++;
	    else if (labels[ego] < 0) straight_labeled_straight++;
	    else straight_unlabeled++;
	  }	    
	}
      }
    }

    cout << total_err << " "
	 <<  gay_labeled_gay << " "
	 <<  gay_labeled_straight << " "
	 <<  gay_unlabeled << " "
	 <<  straight_labeled_gay  << " "
	 <<  straight_labeled_straight << " "
	 <<  straight_unlabeled << " "
	 <<  endl;
    
    double * swap = new_labels;
    new_labels = labels;
    labels = swap;
    return total_err;
  }

};
 

/*
 * Loads node data from input file
 */
int get_nodes (ifstream & file, double * inf, double * new_inf,  int numnodes, int numlabels, int all) {
  int total = 0;
  for (int j = 0; j < numnodes; j++) {
    file >> inf[j];
    new_inf[j] = inf[j];
    total += inf[j];
  }
  if (all == 0) {
    for (int j = numlabels; j < numnodes; j++) {
      new_inf[j] = inf[j] = 0.0;
    }
  }
  return total;
}

int get_nodes (ifstream & file, int * inf, int numlabels) {
  int total = 0;
  for (int j = 0; j < numlabels; j++) {
    file >> inf[j];
    total += inf[j];
  }
  
  return total;
}

/*
 * Initialize and run the sampling loop
 */
void run_mhrw ( const char * input_name, int all, int discrete) {

  ////////////////////////
  //
  // Read in graph data
  //
  char line[1024];
  sprintf (line, "%s.outx", input_name);
  ofstream outfile (line);
  cerr << "outfile: " << line << endl;

  
  ifstream file (input_name);
  cerr << "infile: " << input_name << endl;
  string s;
  int numedges, numnodes, numlabels, numtestlabels;
  file >> s >> numnodes;
  cerr << s << "\t" << numnodes << endl;
  file >> s >> numedges;
  cerr << s  << "\t" << numedges << endl;

  PUNGraph g  = PUNGraph::New ();  

  for (int i = 0; i< numnodes; i++) {
    g->AddNode(i);
  }
  
  int u,v;
  double w;
  THash<TPair<TInt, TInt>, float> edgeweight;
  for (int i = 0; i < numedges; i++) {
    file >> u >> v >> w;
    g->AddEdge(u, v);
    //TUNGraph::TEdgeI ei = g->GetEI(u, v);
    
    edgeweight.AddDat(TPair<TInt, TInt>(min(u,v),max(u,v)), TFlt(w));
  }

  file >> s >> numlabels;
  cout << "num_labels: " << numlabels << endl;
  double * labels = new double[numnodes];
  double * newlabels = new double[numnodes];
  get_nodes (file, labels, newlabels, numnodes, numlabels, all);
  
  file >> s >> numtestlabels;
  cout << "num_test_labels: " << numtestlabels << endl;
  int test_labels[numtestlabels];
  int diff = get_nodes (file, test_labels, numtestlabels);

  
  
  
  cout << "diff: " << diff << endl;
  double numPos = (numtestlabels + diff) / 2.0;
  double numNeg = (numtestlabels - diff) / 2.0;
  cout << numtestlabels << " " << numPos << " " << numNeg <<  endl;

  Model model (g, labels, newlabels, numlabels, edgeweight, numtestlabels, test_labels, discrete);

  int reps = 0;
  //////////////////////////////
  // Main loop
  //
  double err;
  do {
    err = model.tic();
    reps++;
  } while (err > 1 && reps < 10000);
 
}


int main(int argc, char* argv[]) {
 
  TCon console;
  Env = TEnv(argc, argv, TNotify::StdNotify);

  

  const TStr input_name = Env.GetIfArgPrefixStr 
    ("-file:", "", "Input graph filename, without .graph extension");

  const TInt all = Env.GetIfArgPrefixInt 
    ("-all:", 1, "1 = yes use precomputed labels. 0 = only true labels.");

  const TInt discrete = Env.GetIfArgPrefixInt 
    ("-discrete:", 0, "1 = yes flip. 0 = only true labels.");

  
  run_mhrw (input_name(), all, discrete);
}
