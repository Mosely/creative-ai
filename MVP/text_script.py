# Importing Dependencies
import torch
import torch.nn as nn
from torch.autograd import Variable
import unidecode
import pandas as pd
import string
import json
import requests
import random
import re
import time, math

# __________________________________________________________

# Getting characters data
all_characters = string.printable
n_characters = len(all_characters)

# __________________________________________________________


# Setting Inputs and Targets
# Turn string into list of longs
def char_tensor(string):
    tensor = torch.zeros(len(string)).long()
    for c in range(len(string)):
        tensor[c] = all_characters.index(string[c])
    return (tensor)

# __________________________________________________________

# Defining the RNN class

class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, n_layers=1):
        super(RNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_layers = n_layers

        self.encoder = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size, n_layers)
        self.decoder = nn.Linear(hidden_size, output_size)

    def forward(self, input, hidden):
        input = self.encoder(input.view(1, -1))
        output, hidden = self.gru(input.view(1, 1, -1), hidden)
        output, hidden = self.gru(input.view(1, 1, -1), hidden)
        output, hidden = self.gru(input.view(1, 1, -1), hidden)
        output, hidden = self.gru(input.view(1, 1, -1), hidden)
        output, hidden = self.gru(input.view(1, 1, -1), hidden)
        output = self.decoder(output.view(1, -1))
        return output, hidden

    def init_hidden(self):
        return (torch.zeros(self.n_layers, 1, self.hidden_size))

# __________________________________________________________

# Importing Trained Model:

hidden_size = 100
n_layers = 1

decoder = RNN(n_characters, hidden_size, n_characters, n_layers)
decoder.load_state_dict(torch.load('./rnn.py'))


# __________________________________________________________

# Setting up the evaluator
def evaluate(prime_str='A', predict_len=100, temperature=0.8):
    hidden = decoder.init_hidden()
    prime_input = char_tensor(prime_str)
    predicted = prime_str

    # Use priming string to "build up" hidden state
    for p in range(len(prime_str) - 1):
        _, hidden = decoder(prime_input[p], hidden)
        inp = prime_input[-1]

    inp = prime_input[-1]

    for p in range(predict_len):
        output, hidden = decoder(inp, hidden)

        # Sample from the network as a multinomial distribution
        output_dist = output.data.view(-1).div(temperature).exp()
        top_i = torch.multinomial(output_dist, 1)[0]

        # Add predicted character to string and use as next input
        predicted_char = all_characters[top_i]
        predicted += predicted_char
        inp = char_tensor(predicted_char)

    return predicted

# __________________________________________________________

# Setting up Sentiment Analysis
def get_sentiment(string):
    r = requests.post("http://text-processing.com/api/sentiment/", data={'text': string})
    return json.loads(r.text)

def get_candidates(num_candidates=10, predict_len=10, temperature=0.8):
    candidates = []
    # Keep track of how many evaluations we calculate
    sentiment_evaluations = 0
    # Evaluate potential candidated until we have our desired amount
    while len(candidates) != num_candidates:
        prime_str = random.choice(string.ascii_uppercase)
        sample = evaluate(prime_str, predict_len, temperature)

        # With predicted sample, run through sentiment analysis
        sentiment = get_sentiment(sample)
        sentiment_evaluations += 1

        # Finalizing candidate if it has a strong enough score
        if sentiment['probability']['pos'] > 0.60:
            print(sentiment['probability'])
            candidates.append(sample)

        # Stop early if calculate too many evaluations (request limit)
        if sentiment_evaluations >= 2000:
            print("too many attempts: " + str(sentiment_evaluations))
            return candidates

    print("number of sentiment evaluations done: " + str(sentiment_evaluations))
    return candidates
