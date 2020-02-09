EXTERNAL_ASSETS = 0.8
BANK_DEFAULTS = []

class Bank(object):
    def __init__(self, bank_id, interbank_assets=0.2, liabilities=0.96):
        self.bank_id = bank_id
        self.interbank_assets = interbank_assets
        self.liabilities = liabilities
        self.default = False
        self.bank_connected = [] #List of banks it owes money to
        self.bank_lent = 0 #Number of banks owing money from it
        self.edges = [] # Elements of edges: (the bank itself, the bank it borrows money from, the amount of liabilities)

    # For NetworkX to label the bank based on ID.
    def __str__(self):
        return str(self.bank_id)

    # This function is called when the bank connected to 'self' defaults, transmitting its loss to the asset.
    def update_total_assets(self, loss):
        self.interbank_assets -= loss
        global EXTERNAL_ASSETS
        if(EXTERNAL_ASSETS + self.interbank_assets < self.liabilities):
            global BANK_DEFAULTS
            BANK_DEFAULTS.append(self)

    # This function is called every time 'self' borrows money from a new bank.
    def update_connection(self, bank):
        self.bank_connected.append(bank)
        bank.bank_lent += 1

    # This function is called when the bank is set to default.
    def default_bank(self):
        self.default = True
        for bank in self.bank_connected:
            if (bank.default==False):
                bank.update_total_assets(self.interbank_assets/bank.bank_lent)

    def total_assets(self):
        return self.interbank_assets + EXTERNAL_ASSETS

class Graph(object):
    def __init__(self, bank_number=5, average_degree=5, iteration=2):
        self.bank_number = bank_number
        self.average_degree = average_degree
        self.bank_list = []
        self.iteration = iteration
        self.global_cascades = 0
        self.borrow_probability = 0

    # Generate random banks and random connections between banks.
    def generate_bank(self):
        self.borrow_probability = self.average_degree/self.bank_number
        for i in range(self.bank_number):
            newBank = Bank(bank_id=i)
            self.bank_list.append(newBank)
        potential_lender = self.bank_list.copy()

        for bank in self.bank_list:
            for lender in potential_lender:
                import random
                tendency = random.uniform(0, 1) # Generate random number. The lower, the higher chance of a connection.
                if(bank!=lender and tendency < self.borrow_probability):
                    bank.update_connection(lender)

        self.random_default_bank()
        self.print_banks_status()
        if(len(BANK_DEFAULTS)/self.bank_number >= 0.05):
            self.global_cascades += 1

    def draw_graph(self):
        for i in range(0,self.iteration):
            global BANK_DEFAULTS
            BANK_DEFAULTS.clear()
            self.bank_list.clear()
            self.generate_bank()
        self.store_data()

    def print_banks_status(self):
        global BANK_DEFAULTS
        #print("Total Number of Defaults ", len(BANK_DEFAULTS))

    def random_default_bank(self):
        import random
        random_bank = random.choice(self.bank_list)
        #print("The bank chosen to default is Bank" , random_bank.bank_id)
        BANK_DEFAULTS.append(random_bank)
        i = 0
        for i in range(0,len(BANK_DEFAULTS)):
            BANK_DEFAULTS[i].default_bank()

    def store_data(self):
        import json
        average_degree = self.average_degree
        prob_contagion = self.global_cascades/self.iteration
        print("Average Degree : ", average_degree , "Probability of Contagion : ", prob_contagion)
        with open('data.json') as f:
            data = json.loads(f.read())
            data[average_degree] = prob_contagion
            with open('data.json', 'w') as f:
                json.dump(data, f)

import numpy
for i in numpy.arange(0,10,0.5):
    graph = Graph(bank_number=500, average_degree=i, iteration=100)
    graph.draw_graph()

import matplotlib.pyplot as plt
import json
import collections

with open('data.json') as f:
    data = json.loads(f.read())
    x_axis = []
    y_axis = []
    data = dict(sorted(data.items()))
    for key, value in data.items():
        x_axis.append(float(key))
        y_axis.append(float(value))
    plt.plot(x_axis, y_axis)
    plt.axis([0, 10, 0, 1])
    plt.show()
