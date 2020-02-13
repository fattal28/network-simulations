#include <iostream>
#include <stdbool.h>
#include <vector>
#include <map>
#include <algorithm>
#include <random>
#include <ctime>

using namespace std;

float EXTERNAL_ASSETS = 0.8;
map<float,float> DATA;

class Bank{
  float interbank_assets;
  float liabilities;

public:
  Bank(){
    interbank_assets = 0.2;
    liabilities = 0.96;
    defaulted = false;
    bank_lent = 0;
  }
  vector<Bank> bank_connected;
  int bank_id;
  int bank_lent;
  bool defaulted;
  void set_id(int);
  void update_total_assets(float);
  void update_connection(Bank&);
  void default_bank();
  void increment_lent();
};

vector<Bank> BANK_DEFAULTS;

void Bank::set_id(int id){
  bank_id = id;
}

void Bank::update_total_assets(float loss){
  interbank_assets -= loss;
  if(EXTERNAL_ASSETS + interbank_assets < liabilities){
    BANK_DEFAULTS.push_back(*this);
  }
}

void Bank::update_connection(Bank& bank){
  bank.bank_lent += 1;
  bank_connected.push_back(bank);
}

void Bank::default_bank(){
  defaulted = true;
  for(Bank& bank : bank_connected){
    if(!bank.defaulted){
      float loss = (float) interbank_assets / bank.bank_lent;
      bank.update_total_assets(loss);
    }
  }
}

class Graph{
  int bank_number;
  float average_degree;
  vector<Bank> bank_list;
  int iteration;
  float global_cascades;
  float borrow_probability;
  int connection;

public:
  void set_values(int,float,int);
  void generate_bank();
  void draw_graph();
  void random_default_bank();
  void store_data();
};

void Graph::set_values(int number, float degree, int iter){
  bank_number = number;
  average_degree = degree;
  iteration = iter;
}

void Graph::generate_bank(){
  borrow_probability = (float) average_degree/bank_number;
  for(int i=0; i<bank_number; i++){
    Bank newBank = Bank();
    newBank.set_id(i);
    bank_list.push_back(newBank);
  }


  for(int borrow=0; borrow<bank_list.size(); borrow++){
    for(int lend=0; lend<bank_list.size(); lend++){
      float tendency = ((float) rand() / (RAND_MAX));
      if(borrow!=lend && tendency < borrow_probability){
        bank_list[borrow].update_connection(bank_list[lend]);
        connection += 1;
      }
    }
  }

  random_default_bank();
  float default_percentage = (float) BANK_DEFAULTS.size()/bank_number;

  if(default_percentage >= 0.05){
    global_cascades += 1;
  }
}

void Graph::draw_graph(){
  connection = 0;
  for(int i=0; i<iteration; i++){
    BANK_DEFAULTS.clear();
    bank_list.clear();
    generate_bank();
  }
  store_data();
}

void Graph::random_default_bank(){
  float random_zero_to_one = ((float) rand() / (RAND_MAX));
  int random_index = random_zero_to_one * bank_list.size();
  Bank random_bank = bank_list[random_index];
  BANK_DEFAULTS.push_back(random_bank);
  int i = 0;
  while(i<BANK_DEFAULTS.size()){
    BANK_DEFAULTS[i].default_bank();
    i+=1;
  }
}

void Graph::store_data(){
  float prob_contagion = global_cascades / iteration;
  float average_degree = (float) connection / (iteration*bank_number);
  cout << "Average Degree : " << average_degree << " Probability of Contagion : " << prob_contagion << endl;
  DATA.insert({average_degree,prob_contagion});
}

int main(){
  clock_t begin_time = clock();
  for (float i=0; i<10; i+=0.5){
    Graph graph = Graph();
    graph.set_values(100,i,100);
    graph.draw_graph();
  }

  for (auto const& pair: DATA) {
       cout << "{" << pair.first << " : " << pair.second << "}\n";
   }

   cout << "Time Elapsed : " << float( clock () - begin_time ) /  CLOCKS_PER_SEC;

  return 0;
}
