#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#                                                                                                                                                                               #
# Blackbox data collector Bot                                                                                                                                                   #
#                                                                                                                                                                               #
# Copyright © 2023 Team 6                                                                                                                                                       #
#                                                                                                                                                                               #                                                                                                                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”),                            #
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,                            #
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:                                    #
#                                                                                                                                                                               #
# - None, enjoy :D                                                                                                                                                              #
#                                                                                                                                                                               #
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.                                                #
#                                                                                                                                                                               #
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,                           #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,                 #
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                    #
#                                                                                                                                                                               #
# Author: Mario Franco                                                                                                                                                          #
#                                                                                                                                                                               #
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

import os
import ray
import time
import requests
import numpy as np
from ray.experimental.tqdm_ray import tqdm
from datetime import datetime
from html.parser import HTMLParser

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Extracted classes and color from the website

ORG_MAP = {'bru': 0, 'gru': 1, 'hkg': 2, 'icn': 3, 'jfk': 4, 'las': 5, 'lax': 6, 'lis': 7, 'mex': 8, 'pty': 9}
INV_MAP = {0: 'bru',  1: 'gru', 2: 'hkg', 3: 'icn', 4: 'jfk', 5: 'las', 6: 'lax', 7: 'lis', 8: 'mex', 9: 'pty'}
COLOR_MAP = {0: '#999933',  1: '#000000', 2: '#CC6677', 3: '#882255', 4: '#44AA99', 5: '#4141FF', 6: '#117733', 7: '#AA4499', 8: '#FFFFFF', 9: '#88CCEE'}

TRUE_MAP = {1:0, 9:1, 4:2, 6:3, 5:4, 7:5, 0:6, 2:7, 3:8, 8:9}
TRUE_COLOR_MAP = {6: '#999933',  0: '#000000', 7: '#CC6677', 8: '#882255', 2: '#44AA99', 4: '#4141FF', 3: '#117733', 5: '#AA4499', 9: '#FFFFFF', 1: '#88CCEE'}

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def get_blackbox_cmap():
    """
    Get Blackbox Cmap

    A helper method to recover the original color map for the blackbox
    """
    from matplotlib import pyplot as plt
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(COLOR_MAP.values())
    return cmap

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class BlackboxParser(HTMLParser):
    """
    Blackbox Parser

    Auxiliary class to parse the relevant data from the GET request.
    """

    def __init__(self, **kwargs):
        super(BlackboxParser, self).__init__(**kwargs)
        self._blackbox = []
        self._row = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for a in attrs:
                if a[0] == 'id' and a[0] == 'controls':
                    print(attrs)

        if tag == 'td':
            for a in attrs:
                if a[0] == 'class':
                    self._row.append(a[1])
                    break

    def handle_endtag(self, tag):
        if tag == 'tr':
            self._blackbox.append(self._row)
            self._row = []

    def blackbox(self):
        return np.array(self._blackbox, dtype=object)

    def clear(self):
        self._blackbox = []
        self._row = []

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# The core of the blackbox bot.

@ray.remote
class BlackBoxBot:
    """
    Blackbox Bot

    Agent used to collect data from \"https://casci.binghamton.edu/academics/ssie501/blackbox/BlackBox.php\".

    This agent advances a single step and then returns to the previous state to collect as many transitions from a given initial state as indicated.
    # IMPORTANT: This is a ray agent so it requires the ray interface to use manually use it. A simplified version can be obtained by commenting the tag \"@ray.remote\".

    Parameters:
    - size: number of transitions to sample
    - output_folder: output folder to save the numpy file. default: \"./\"
    - stepsize: number of consecutive transitions requested. Sizes larger than 1 may produce transitions that are harder to track. default: \"1\"
    - prewarm: number of transitions before starting to record data. default: \"0\"
    - worker_id: number designed to this specific worker. default: \"0\"
    - revert: indicates whether the bot should return to the initial_state or not. default: True
    - reset_after_step: indicates whether the bot should reset the blackbox after taking a step. default: False

    Output:
    - data: this worker returns a numpy array with the shape (size, 2, 20, 20). Where the axis 0 denotes the requested transitions, the axis 1, the prior and
            posterior state, and the axis 2 and 3 the actual data.
    - file: this worker also export the aforementioned data to a numpy file into the specified output_folder

    Methods:
    - reset(): reset the blackbox agent to a clean state.
    - collect(): start the data collection process.
    """

    def __init__(self, size, output_folder='./', stepsize=1, prewarm=0,  revert=True, reset_after_step=False, worker_id=0):
        assert not (revert and reset_after_step), '"revert" and "reset_after_step" cannot be True at the since time.'
        self._reset_after_step = reset_after_step
        self._revert = revert
        self._worker_id = worker_id
        self._size = size
        self._prewarm = prewarm
        self._parser = BlackboxParser()
        self._session = requests.Session()
        self._output_folder = output_folder
        self._url = 'https://casci.binghamton.edu/academics/ssie501/blackbox/BlackBox.php'
        self._step_url = f'https://casci.binghamton.edu/academics/ssie501/blackbox/BlackBox.php?cycles={stepsize}'
        self._prewarm_url = f'https://casci.binghamton.edu/academics/ssie501/blackbox/BlackBox.php?cycles={prewarm}'
        self._revert_url = f'https://casci.binghamton.edu/academics/ssie501/blackbox/BlackBox.php?revert={stepsize}&cycles_input={stepsize}'
        self._reset_url = f'https://casci.binghamton.edu/academics/ssie501/blackbox/BlackBox.php?reset=1&cycles_input={stepsize}'
        self._map_dict = ORG_MAP
        self._map = lambda x : np.vectorize(self._map_dict.get)(x)
        # Initialize bot
        self._session = requests.Session()
        self.reset()

    def reset(self, clear_buffer=True): 
        # Clear buffer
        if clear_buffer:
            self._data = np.zeros((self._size, 2, 20, 20), dtype=int)
        # Start the session
        request = self._session.get(self._reset_url)
        if self._prewarm > 0:
            request = self._session.get(self._prewarm_url)
        self._parser.clear()
        self._parser.feed(request.text)

    def _step(self, s): 
        # Save prior state
        self._data[s,0] = self._map(self._parser.blackbox())
        # Forward step
        request = self._session.get(self._step_url)
        # Save posterior state
        self._parser.clear()
        self._parser.feed(request.text)
        self._data[s,1] = self._map(self._parser.blackbox())
        # Perform a revert or reset step if neccesary
        if self._revert:
            request = self._session.get(self._revert_url)
            self._parser.clear()
            self._parser.feed(request.text)
        elif self._reset_after_step:
            self.reset(clear_buffer=False)
    
    def _save_to_numpy(self):
        filename = f'blackbox_1_step_{int(datetime.now().timestamp())}_bot_{self._worker_id}'
        path = os.path.join(self._output_folder, filename)
        np.save(path, self._data)
        print(f'BotID:{self._worker_id} \t File successfully saved at: {filename}')
    
    def collect(self):
        #for s in range(self._size):
        progress_bar = tqdm(desc=f'Collecting', total=self._size, position=self._worker_id)
        for s in range(self._size):
            self._step(s)
            progress_bar.update(1)
        self._save_to_numpy()
        return self._data

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

class BotsHandler():
    """
    Bots Handler

    Wrapper class used to manage multiple Blackbox Bots at the same time.
    """
    def __init__(self, size, num_workers, output_folder='./', stepsize=1, prewarm=0, revert=True, reset_after_step=False):
        # Create directory if do not exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Create workers
        self._num_workers = num_workers
        self._workers = [BlackBoxBot.remote(size, output_folder=output_folder, stepsize=stepsize, prewarm=prewarm, revert=revert, reset_after_step=reset_after_step, worker_id=i) for i in range(self._num_workers)]


    def collect(self):
        collect = [self._workers[i].collect.remote() for i in range(self._num_workers)]
        ray.get(collect)
        return collect

    def reset(self):
        reset = [self._workers[i].collect.reset() for i in range(self._num_workers)]
        ray.get(reset)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#