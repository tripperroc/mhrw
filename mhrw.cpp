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
  double gayweight; // Weight of gay data
  double labweight; // Weight of labeled data
  int numlabels;
  THash<TPair<TInt, TInt>, float> edgeweight;
  double edges_weight;
  double classes_weight;
  double edges_total;
  double edges_part;
  float edges_divisor;
  float new_edges_divisor;
  double imbalance_error;
  double imbalance_error_diff;
  double * node_total_similarity;
  double * node_diff_similarity;
  double edges_diff;
  double * stats;
  int num_swaps;
  int * changes;
  TFlt new_imbalance_error;
  double total_gay;
  double gay_diff;
  double * times_gay;
public:
  int * temp_labels;
  int * labels;
  double gay_fraction;
  double target_gay_fraction;
  long num_times;
  
  Model (PUNGraph p, int * labels, double gayweight, double labweight, int numlabels, THash<TPair<TInt, TInt>, float> edgeweight, double edges_weight, double classes_weight): p(p), labels(labels), gayweight(gayweight), labweight(labweight), numlabels(numlabels), edgeweight(edgeweight), edges_weight(edges_weight), classes_weight(classes_weight), target_gay_fraction(.1), num_times(0) {
    temp_labels = new int[p->GetNodes()];
    edge_weights = new double[p->GetNodes()];
    node_total_similarity = new double[p->GetNodes()];
    node_diff_similarity = new double[p->GetNodes()];
    stats = new double[p->GetNodes()];
    times_gay = new double[p->GetNodes()];
    
    for (int i = 0; i < p->GetNodes(); i++) {
      temp_labels [i] = 0;
      node_diff_similarity[i] = 0;
      times_gay[i] = 0;
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

  void poll () {
    for (int i = 0; i < p->GetNodes(); i++) {
      times_gay[i] += float(labels[i]);
    }
    num_times++;
  }

  void report ( int numtestlabels, int * test_labels){
    for (int i = 0; i < p->GetNodes(); i++) {
      times_gay[i] = times_gay[i] / float(num_times);
      //cout << times_gay[i] << endl;
    }

    for (float thresh = -1.01; thresh <= 1.01; thresh += .02) {
      cout << thresh << " ";

     int gay_labeled_gay = 0,
       gay_labeled_straight = 0,
       gay_unlabeled = 0,
       straight_labeled_straight = 0,
       straight_labeled_gay = 0,
       straight_unlabeled = 0;

     for (int ego = numlabels; ego < numlabels + numtestlabels; ego++) {
 
       TInt ego2 = ego - numlabels;
       if (test_labels[ego2] > 0) {
	 if (times_gay[ego] > thresh) gay_labeled_gay++;
	 else if (times_gay[ego] <= thresh) gay_labeled_straight++;
	 else gay_unlabeled++;
       }
       if (test_labels[ego2] <= 0) {
	 if (times_gay[ego] > thresh) straight_labeled_gay++;
	 else if (times_gay[ego] <= thresh) straight_labeled_straight++;
	 else straight_unlabeled++;
       }	    
     }
     double accuracy, f, precision, recall, true_positive, false_positive;
     
     accuracy = float(gay_labeled_gay + straight_labeled_straight) / float(gay_labeled_gay + straight_labeled_gay + gay_labeled_straight + straight_labeled_straight);
     
     if (gay_labeled_gay + straight_labeled_gay == 0)
       precision = 0.0;
     else
       precision = float(gay_labeled_gay) / float (gay_labeled_gay + straight_labeled_gay);
     if (gay_labeled_gay + gay_labeled_straight == 0)
       recall = 0.0;
     else
       recall = float(gay_labeled_gay)/ float(gay_labeled_gay + gay_labeled_straight);
     if (straight_labeled_gay + straight_labeled_straight == 0)
       false_positive = 0.0;
     else
       false_positive = float(straight_labeled_gay)/float(straight_labeled_gay + straight_labeled_straight);
     if (gay_labeled_gay + gay_labeled_straight == 0)
       true_positive = 0.0;
     else
       true_positive = float(gay_labeled_gay)/float(gay_labeled_gay + gay_labeled_straight);
     if (precision + recall == 0)
       f = 0;
     else
       f = 2.0 * precision * recall / (precision + recall);
     
     cout <<  gay_labeled_gay << " "
	  <<  gay_labeled_straight << " "
	  <<  gay_unlabeled << " "
	  <<  straight_labeled_gay  << " "
	  <<  straight_labeled_straight << " "
	  <<  straight_unlabeled << " "
	  <<  accuracy << " "
	  <<  f << " "
	  <<  precision << " "
	  <<  recall << " "
	  <<  true_positive << " "
	  <<  false_positive
	  <<  endl;
    }
  }
  /*
   * Calculates the log probability of a given label set
   */
  double getLogProb  (int * labels) {
    TInt u,v;

    total_gay = 0;
    edges_total = 0;
    edges_divisor = 0;
    int new_label_totals = 0;
    for (TUNGraph::TNodeI n = p->BegNI(); n != p->EndNI(); n++) {
      
      TInt ego = n.GetId();

      node_total_similarity[ego] = 0;
      if (labels[ego] != this->labels[ego]) new_label_totals++;
      
      float subtotal = 0;
      TInt neighborhood_size = n.GetDeg();
      double neighborhood_weight = 0;
      for (int i = 0; i < neighborhood_size; i++) {
	
	TInt alter = n.GetNbrNId(i);
	double neighbor_weight = edgeweight.GetDat(TPair<TInt, TInt>(min(ego,alter), max(ego,alter)));
	node_total_similarity[ego] +=  neighbor_weight * diff(ego, alter, labels); // / edge_weights[ego];
	neighborhood_weight += neighbor_weight;

      }
      subtotal = node_total_similarity[ego] / edge_weights[ego];
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
    edges_part = edges_weight * edges_total /  edges_divisor;
    gay_fraction = double(total_gay) / double(p->GetNodes());
    imbalance_error = target_gay_fraction - gay_fraction;
    double classes_part = classes_weight * imbalance_error * imbalance_error;
    // cout << "Oink Oink" << endl;
    //cerr << edges_weight << " " << edges_total << " "  << edges_divisor  << " " << edges_part << " " << classes_part << " " << gay_fraction << " ";
    return -edges_part - classes_part ;
  }

  void setTemp (int position, int val) {
      temp_labels[position] = val;
  }

  double diff(TInt ego, TInt alter, int * labels) {
    int ego_label = labels[ego] != 0 ? labels[ego] : this->labels[ego];
    int alter_label = labels[alter] != 0 ? labels[alter] : this->labels[alter];
    double diff = ego_label - alter_label;
    return  diff * diff / 4;
  }
	 
  double getLogDiff (int num_swaps, int * changes) {
    this->num_swaps = num_swaps;
    this->changes = changes;
    edges_diff = 0;
    gay_diff = 0;
    int new_label_totals = 0;
    double tot_diffs = 0;
    new_edges_divisor = edges_divisor;
    for (int i = 0; i < num_swaps; i++) {
      TInt ego = changes[i];
      if (temp_labels[ego] != labels[ego]) {
	
	
	TUNGraph::TNodeI n = p->GetNI(ego);

	node_diff_similarity[ego] = 0;
	TInt neighborhood_size = n.GetDeg();
	for (int i = 0; i < neighborhood_size; i++) {
	  
	 
	  TInt alter = n.GetNbrNId(i);
	  double neighbor_weight = edgeweight.GetDat(TPair<TInt, TInt>(min(ego,alter), max(ego,alter)));
	  double difference = diff(ego,alter,temp_labels) - diff(ego,alter,labels);
	  node_diff_similarity[ego] += neighbor_weight * difference;
	  new_label_totals++;
	  tot_diffs +=   neighbor_weight * diff(ego, alter, temp_labels) / edge_weights[ego]; //neighbor_weight;
	  if (temp_labels[alter] == 0 || temp_labels[alter] == this->labels[alter]) {
	    TFlt alter_factor = 1;
	    
	    if (temp_labels[alter] == 1 || (temp_labels[alter] == 0 && this->labels[alter] == 1) ) {
	      alter_factor = gayweight;
	    }
	    if (alter < numlabels) {
	      alter_factor *= labweight;
	    }
	    edges_diff +=  alter_factor * neighbor_weight * difference / edge_weights[alter];
	    
	    node_diff_similarity[alter] += neighbor_weight * difference;
	    new_label_totals++;
	    tot_diffs += alter_factor * neighbor_weight * diff(ego, alter, temp_labels) / edge_weights[alter]; // neighbor_weight;

	  }
	}
	 
	if (temp_labels[ego] == 1) {

	  edges_diff += (gayweight * (node_total_similarity[ego] + node_diff_similarity[ego]) - node_total_similarity[ego]) / edge_weights[ego];
	  gay_diff += 1;
	  new_edges_divisor += (gayweight - 1);
	}
	else {
	 
	  
	  edges_diff += (node_total_similarity[ego] + node_diff_similarity[ego] - gayweight * node_total_similarity[ego]) / edge_weights[ego];
	  gay_diff -= 1;
	  new_edges_divisor -= (gayweight - 1);
	}
	 

      }
      
    }
    //cout << "gay_diff: " << gay_diff << ", size: " << double(p->GetNodes()) << endl;
    TFlt new_gay_frac = gay_fraction + gay_diff / double(p->GetNodes());
    new_imbalance_error = target_gay_fraction - new_gay_frac;
    imbalance_error_diff = new_imbalance_error * new_imbalance_error - imbalance_error * imbalance_error;

    //cout  << new_label_totals << " " << tot_diffs << " " <<
    // cout << edges_weight << " " << edges_total + edges_diff << " " << new_edges_divisor << " " ;
    //cerr << edges_weight * (edges_total + edges_diff) /  new_edges_divisor << " ";
    //cerr <<  classes_weight * new_imbalance_error * new_imbalance_error << " ";
    //cerr << new_gay_frac << " ";
    //cerr <<  (- edges_weight * edges_diff/new_edges_divisor  - classes_weight * imbalance_error_diff) << " ";
    //return  - edges_weight * edges_diff/new_edges_divisor  - classes_weight * imbalance_error_diff;
    return  - (edges_weight * ((edges_divisor-new_edges_divisor) * edges_total + edges_divisor * edges_diff)  /(new_edges_divisor * edges_divisor))  - classes_weight * imbalance_error_diff;

  }
  
  void accept () {
    
    for (int i = 0; i < num_swaps; i++) {
      TInt ego = changes[i];
      labels[ego] = temp_labels[ego];
      temp_labels[ego] = 0;
       
    
      if (temp_labels[ego] != labels[ego]) {
	
	node_total_similarity[ego] += node_diff_similarity[ego];
	node_diff_similarity[ego] = 0;
	
	TUNGraph::TNodeI n = p->GetNI(ego);
	TInt neighborhood_size = n.GetDeg();
	for (int i = 0; i < neighborhood_size; i++) {
	  	 
	  TInt alter = n.GetNbrNId(i);
	  node_total_similarity[alter] += node_diff_similarity[alter];
	  node_diff_similarity[alter] = 0;
	}
      }
    }
    imbalance_error = new_imbalance_error;
    edges_total += edges_diff;
    gay_fraction = gay_fraction + gay_diff / double(p->GetNodes());
    edges_divisor = new_edges_divisor;
    //cout  << edges_total / new_edges_divisor << " ( " <<
    //  -edges_weight * edges_total / edges_divisor  - classes_weight *imbalance_error*imbalance_error
    //	  << " ) " << endl;
    // cout << "***** accepted *****" << endl;

  }
  
  void reject () {
    
    for (int i = 0; i < num_swaps; i++) {
      TInt ego = changes[i];
      temp_labels[ego] = 0;
      if (temp_labels[ego] != labels[ego]) {
	
	node_diff_similarity[ego] = 0;
	
	TUNGraph::TNodeI n = p->GetNI(ego);
	TInt neighborhood_size = n.GetDeg();
	for (int i = 0; i < neighborhood_size; i++) {
	  	 
	  TInt alter = n.GetNbrNId(i);
	  node_diff_similarity[alter] = 0;
	}
      }

    }
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
 * Loads node data from input file
 */
int get_nodes (ifstream & file, int * inf,  int numnodes, long * names) {
  int total = 0;
  //long la;
  for (int j = 0; j < numnodes; j++) {
    file >> names[j] >> inf[j];
    //cerr << names << " " << inf[j] << endl;
    //saved_inf[j] = new_inf[j] = inf[j];
    total += inf[j];
  }
  /*if (all == 0) {
    for (int j = numlabels; j < numnodes; j++) {
      inf[j] = 0.0;
    }
    }*/
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
  cerr << "num_nodes: " << numnodes << endl;
  int * labels = new int[numnodes];
  long * names = new long[numnodes];
  
  get_nodes (file, labels, numnodes, names);
 
  file >> s >> numtestlabels;
  cerr << "num_test_labels: " << numtestlabels << endl;
  int test_labels[numtestlabels];
  int diff = get_nodes (file, test_labels, numtestlabels);
  cerr << "diff: " << diff << endl;
  double numPos = (numtestlabels + diff) / 2.0;
  double numNeg = (numtestlabels - diff) / 2.0;
  cerr << numtestlabels << " " << numPos << " " << numNeg <<  endl;

  Model model (g, labels, gayweight, labweight, numlabels, edgeweight, edges_weight, classes_weight);

  double lastProb = model.getLogProb(labels);
  //cerr << endl;
  double minProb = lastProb;
 
  //long iterations = 0;
  
  
  //////////////////////////////
  // Main loop
  //
  for (long iterations = 0; iterations < 100000; iterations++) {

    /////////////////////////////////////
    // Make a copy of the current labels
    //
    //int * temp_labels = new int[numnodes];
    
    /*
    for (int i = 0; i< numnodes; i++) {
      model.temp_labels[i] = model.labels[i];
      
    }
    */
    
    /////////////////////////////////
    // Choose nodes to change
    //
    int changes[num_swaps];
    choose (numnodes - numlabels, num_swaps, changes);
    /*
    // DEBUG
    for (int i = 0; i < num_swaps; i++) {
      changes[i] = numlabels + i;
    }
    */
    double condiff = 1;  // Stores p(x | x') / p(x' | x)
    int gayswap = 0, straightswap = 0;
    TFlt balance;
    if (ballance < 0) {
      balance = .1 * model.target_gay_fraction + .9 * model.gay_fraction;
    }
    else balance = ballance;
    for (int i = 0; i < num_swaps; i++) {
      int ego = changes[i] + numlabels;
      changes[i] += numlabels;
      if (flip == 1) {
	
	model.temp_labels[ego] = -model.labels[ego];
      }
      else {
	if (my_random.GetUniDev () < balance) {
	  model.temp_labels[ego] = 1;
	  if (model.temp_labels[changes[i]] != model.labels[changes[i]]) gayswap++;
	}
	else {
	  model.temp_labels[ego] = -1;
	  if (model.temp_labels[changes[i]] != model.labels[changes[i]]) gayswap--;
	}
	condiff *= ((.5 + (balance - .5) * model.labels[ego]) / 
		    (.5 + (balance - .5) * model.temp_labels[ego]));
      }
      //cout << model.temp_labels[ego] << " ";
    }
     
    //cout << endl;

  
 

    
    /////////////////////////////
    //
    // Test accuracy against test set
    //
    int correctPos = 0;
    int correctNeg = 0;
    for (int i = numlabels; i < numlabels + numtestlabels; i++) {
      if (test_labels[i-numlabels] == model.labels[i]) {
	if (model.labels[i] == 1) {
	  correctPos += 1;
	}
	else {
	  correctNeg += 1;
	}
      }
    }
    //cout <<  "Correct/Num Pos/Neg: " << correctPos << " " <<  correctNeg << " " << numPos << " " << numNeg << endl;
    ///////////////////////
    //
    // Determine whether or not to swap
    //
    //double newProb = model.getLogProb(model.temp_labels);
    //double diffy  = newProb - lastProb;
    double diffy =  model.getLogDiff(num_swaps, changes);
    // cout << "( " << lastProb << " ) ";
    double probDif = exp(diffy);
    double probRat = probDif * condiff ;
    TFlt prob = my_random.GetUniDev ();
    

    if (iterations % 1000 == 0) {
     cerr << diffy << " ";
     cerr  <<  gayswap << " " << probDif <<  " " <<  probRat << " " << prob << " " << minProb << " "
	    << lastProb << " " << (correctPos/numPos) << " " << (correctNeg/numNeg) << " " << greedy << endl;
      cerr << flush;
    }

    if (iterations % 1000 == 0) {
      model.poll();
    }
    
    
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
    
    if ((greedy == 1 && probDif > 1) || (greedy == 0 && prob < probRat)) {
      /*
      int * swap = model.labels;
      model.labels = model.temp_labels;
      model.temp_labels = swap;
      lastProb = newProb;
      */
      lastProb += diffy;
      model.accept();
    }
    else {
       model.reject();
    }
   
    minProb = lastProb > minProb ? lastProb : minProb;
  }
  model.report(numtestlabels, test_labels);
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
