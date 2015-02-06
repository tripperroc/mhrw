#include <iostream>
#include <fstream>
#include <sstream>
#include <math.h>
//#include <time>
#include "Snap.h"



using namespace std;

static TRnd my_random ((int) time(NULL));

class Model {

private:
  PUNGraph p;
  double * edge_weights;
  double gayweight; // Weight of gay data
  double labweight; // Weight of labeled data
  int numlabels;
  THash<TPair<TInt, TInt>, float> edgeweight;
  double edges_weight;
  double classes_weight;
  double edges_total;
  float edges_divisor;
  double imbalance_error;
  double imbalance_error_diff;
  double edges_diff;
  
public:
  int * temp_labels;
  int * labels;
  double gay_fraction;
  double target_gay_fraction;
  
  Model (PUNGraph p, int * labels, double gayweight, double labweight, int numlabels, THash<TPair<TInt, TInt>, float> edgeweight, double edges_weight, double classes_weight): p(p), labels(labels), gayweight(gayweight), labweight(labweight), numlabels(numlabels), edgeweight(edgeweight), edges_weight(edges_weight), classes_weight(classes_weight), target_gay_fraction(.1) {
    temp_labels = new int[p->GetNodes()];
    edge_weights = new double[p->GetNodes()];
    for (int i = 0; i < p->GetNodes(); i++) {
      temp_labels [i] = 0;
    }
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
    delete temp_labels;
  }
  /*
   * Calculates the log probability of a given label set
   */
  double getLogProb  (int * labels) {
    TInt u,v;

    double total_gay = 0;
    edges_total = 0;
    edges_divisor = 0;
    for (TUNGraph::TNodeI n = p->BegNI(); n != p->EndNI(); n++) {
      
      TInt ego = n.GetId();
      float subtotal = 0;
      TInt neighborhood_size = n.GetDeg();
      double neighborhood_weight = 0;
      for (int i = 0; i < neighborhood_size; i++) {
	
	TInt alter = n.GetNbrNId(i);
	double neighbor_weight = edgeweight.GetDat(TPair<TInt, TInt>(min(ego,alter), max(ego,alter)));
	subtotal +=  neighbor_weight * diff(ego, alter, labels);
	neighborhood_weight += neighbor_weight;

      }
      subtotal = subtotal / neighborhood_weight;
      double weight = 1;
      if (labels[ego] == 1) {
	subtotal *= gayweight;
	weight *= gayweight;
	total_gay += 1;
      }
      if (ego < numlabels) {
	subtotal *= labweight;
	weight *= labweight;
      }
      edges_divisor += weight;
      edges_total += subtotal;
    }
    //double edges_part = edges_weight * total / divisor;
    double edges_part = edges_weight * edges_total /  edges_divisor;
    gay_fraction = double(total_gay) / double(p->GetNodes());
    imbalance_error = target_gay_fraction - gay_fraction;
    double classes_part = classes_weight * imbalance_error * imbalance_error;
    cout << edges_part << " " << classes_part << " " << total_gay << " " << gay_fraction << " ";
    return -edges_part - classes_part ;
  }

  void setTemp (int position, int val) {
      temp_labels[position] = val;
  }

  double diff(TInt ego, TInt alter, int * labels) {
    double diff = labels[ego] - labels[alter];
    return  diff * diff / 4;
  }
	 
  double getLogDiff (int num_swaps, int * changes) {
    double edges_diff = 0;
    double gay_diff = 0;
    for (int i = 0; i < num_swaps; i++) {
      TInt ego = changes[i];
      if (temp_labels[ego] != labels[ego]) {
	TFlt ego_factor = 1;
	if (temp_labels[ego] == 1) {
	  gay_diff += 1;
	  ego_factor = gayweight;
	}
	else gay_diff -= 1;
	TUNGraph::TNodeI n = p->GetNI(ego);
	TInt neighborhood_size = n.GetDeg();
	for (int i = 0; i < neighborhood_size; i++) {
	
	  TInt alter = n.GetNbrNId(i);
	  double neighbor_weight = edgeweight.GetDat(TPair<TInt, TInt>(min(ego,alter), max(ego,alter)));
	  double difference = diff(ego,alter, labels) - diff(ego,alter,temp_labels);
	  
	  edges_diff += ego_factor * neighbor_weight * difference / edge_weights[ego];
	  if (temp_labels[alter] == 0 || temp_labels[alter] == labels[alter]) {
	    TFlt alter_factor = 1;
	    if (temp_labels[alter] == 1) {
	      alter_factor = gayweight;
	    }
	    if (alter < numlabels) {
	      alter_factor *= labweight;
	    }
	    edges_diff +=  alter_factor * neighbor_weight * difference / edge_weights[alter];
	  }
	}

      }
      
    }
    TFlt new_gay_frac = gay_fraction + gay_diff / double(p->GetNodes());
    TFlt new_imbalance_error = target_gay_fraction - new_gay_frac;
    imbalance_error_diff = new_imbalance_error * new_imbalance_error - imbalance_error * imbalance_error;
    edges_diff = classes_weight;
    return  edges_weight * edges_diff /  edges_divisor + classes_weight * imbalance_error_diff;

  }
  
  
};

/*
 * Samples a list without replacement
 */
void choose (const TInt & larger, const TInt & smaller, int * data) {

  THash <TInt, TInt> hits; // = new THash <TInt, TInt> ();

  for (int i = 0; i < larger; i++) {

      hits.AddDat(i,i);
  }

  for (int i = 0; i < smaller; i++) {

    TInt chosen = my_random.GetUniDevInt (larger - i);
    data[i] = hits[chosen];
    hits.AddDat(chosen, hits[larger - i - 1]);
  }
}


/*
 * Loads node data from input file
 */
int get_nodes (ifstream & file, int * inf, int numnodes) {
  int total = 0;
  for (int j = 0; j < numnodes; j++) {
    file >> inf[j];
    total += inf[j];
  }
  return total;
}

/*
 * Initialize and run the sampling loop
 */
void run_mhrw ( const char * input_name, int num_swaps, int flip, TFlt ballance, double gayweight, double labweight, int greedy, double edges_weight, double classes_weight) {

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
  cout << "num_nodes: " << numnodes << endl;
  int * labels = new int[numnodes];
  get_nodes (file, labels, numnodes);
  
  file >> s >> numtestlabels;
  int temp_labels[numtestlabels];
  int diff = get_nodes (file, temp_labels, numtestlabels);
  double numPos = (numtestlabels + diff) / 2.0;
  double numNeg = (numtestlabels - diff) / 2.0;
  cout << numtestlabels << " " << numPos << " " << numNeg <<  endl;

  Model model (g, labels, gayweight, labweight, numlabels, edgeweight, edges_weight, classes_weight);

  double lastProb = model.getLogProb(labels);
  int minProb = lastProb;
 
  long iterations = 0;
  
  
  //////////////////////////////
  // Main loop
  //
  while (true) {

    /////////////////////////////////////
    // Make a copy of the current labels
    //
    //int * temp_labels = new int[numnodes];
    for (int i = 0; i< numnodes; i++) {
      model.temp_labels[i] = model.labels[i];
      
    }

    /////////////////////////////////
    // Choose nodes to change
    //
    int changes[num_swaps];
    choose (numnodes - numlabels, num_swaps, changes);
    double condiff = 1;  // Stores p(x | x') / p(x' | x)
    int gayswap = 0, straightswap = 0;
    TFlt balance;
    if (ballance < 0) {
      balance = .1 * model.target_gay_fraction + .9 * model.gay_fraction;
    }
    else balance = ballance;
    for (int i = 0; i < num_swaps; i++) {
      changes[i] += numlabels;
      if (flip == 1) {
	model.temp_labels[changes[i]] *= -1;
      }
      else {
	if (my_random.GetUniDev () < balance) {
	  model.temp_labels[changes[i]] = 1;
	  gayswap++;
	}
	else {
	  model.temp_labels[changes[i]] = -1;
	  straightswap++;
	}
	condiff *= ((.5 + (balance - .5) * model.labels[changes[i]]) / 
		    (.5 + (balance - .5) * model.temp_labels[changes[i]]));
      }
     
    }
    
    /////////////////////////////
    //
    // Test accuracy against test set
    //
    int correctPos = 0;
    int correctNeg = 0;
    for (int i = numlabels; i < numlabels + numtestlabels; i++) {
      if (temp_labels[i - numlabels] == model.labels[i]) {
	if (model.labels[i] == 1) {
	  correctPos += 1;
	}
	else {
	  correctNeg += 1;
	}
      }
    }
    
    ///////////////////////
    //
    // Determine whether or not to swap
    //
    double newProb = model.getLogProb(model.temp_labels);
    double probRat = exp(TFlt(newProb - lastProb)) * condiff ;
    TFlt prob = my_random.GetUniDev ();
    if (iterations % 1 == 0) {
      cout << lastProb << " " << newProb << " " << straightswap << " " <<  gayswap << " " << exp(TFlt(newProb - lastProb)) <<  " " <<  probRat << " " << prob << " " << minProb << " " << (correctPos/numPos) << " " << (correctNeg/numNeg) << " " << greedy << endl;
      cout << flush;
    }
    iterations++;
    
    /*
    // uncomment me to print out the values of all nodes.
    int cnt = 0;
    totals++;
    for (TUNGraph::TNodeI n = g->BegNI(); n != g->EndNI(); n++) {
      cout << labels[n.GetId()] << " ";
      cnt += labels[n.GetId()];
    }
    counts[cnt + numnodes]++;
    cout << lastProb << " " << (counts[cnt + numnodes]/totals) << endl;
    */
    
    if ((greedy == 1 && exp(TFlt(newProb - lastProb)) > 1) || (greedy == 0 && prob < probRat)) {
      //delete labels;
      int * swap = model.labels;
      model.labels = model.temp_labels;
      model.temp_labels = swap;
      lastProb = newProb;
    }
    /*else {
      delete temp_labels;
    }
    */
    minProb = lastProb < minProb ? lastProb : minProb;
  }
  
}


int main(int argc, char* argv[]) {
 
  TCon console;
  Env = TEnv(argc, argv, TNotify::StdNotify);

  const TInt num_swaps = Env.GetIfArgPrefixInt 
    ("-num_swaps:", 10, "No. of nodes to swap at each step.");

  const TInt flip = Env.GetIfArgPrefixFlt 
    ("-flip:", 1, "1 = always flip. 0 = According to balance rate.");

  const TInt greedy = Env.GetIfArgPrefixFlt 
    ("-greedy:", 0, "1 = Use greedy stochastic search. 0 = Use MHRW search.");

  const TFlt balance = Env.GetIfArgPrefixFlt 
    ("-balance:", .5, "Fraction of positive value examples");

  const TFlt edges_weight = Env.GetIfArgPrefixFlt 
    ("-edges:", 1, "weight of edge constraints");
  
  const TFlt classes_weight = Env.GetIfArgPrefixFlt 
    ("-classes:", 1, "weight of class constraints");

  const TFlt gayweight = Env.GetIfArgPrefixFlt 
    ("-gayweight:", 1, "factor by which disagreement with gay ego outweigh straight ego");

  const TFlt labweight = Env.GetIfArgPrefixFlt 
    ("-labweight:", 1, "factor by which disagreement with labeled ego outweigh unlabeled ego");

  

  const TStr input_name = Env.GetIfArgPrefixStr 
    ("-file:", "", "Input graph filename, without .graph extension");

  
  run_mhrw (input_name(), num_swaps, flip, balance, gayweight, labweight, greedy, edges_weight, classes_weight);
}
