from __future__ import division

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np

def parse_cfg(cfgfile):

    # Takes a configuration file

    # Returns a list of blocks. Each blocks describes a block in the neural
    # network to be built. Block is represented as a dictionary in the list

    file = open(cfgfile, 'r')
    lines = file.read().split('\n') # Store lines in list
    lines = [x for x in lines if len(x) > 0] # Get rid of empty lines
    lines = [x for x in lines if x[0] != '#'] # get rid of comments
    lines = [x.rstrip().lstrip() for x in lines] # get rid of fringe whitespace
