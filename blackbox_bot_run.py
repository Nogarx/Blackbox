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
os.environ["RAY_DEDUP_LOGS"] = "0"
os.environ["RAY_TQDM_PATCH_PRINT"] = "1"
import ray
import argparse
from blackbox_bot import BotsHandler

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def run_bots(size, num_workers, output_folder, stepsize, prewarm, revert, reset_after_step):
    assert not (revert and reset_after_step), '"revert" and "reset_after_step" cannot be True at the since time.'
    ray.init()
    bots_handler = BotsHandler(size, num_workers, output_folder=output_folder, stepsize=stepsize, prewarm=prewarm, revert=revert, reset_after_step=reset_after_step)
    bots_handler.collect()
    ray.shutdown()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('--size', type=int, help='Number of transitions to sample')
    parser.add_argument('--num_workers', type=int, help='Number of workers (copies)')
    parser.add_argument('--output_folder', type=str, default='./', help='Output folder')
    parser.add_argument('--stepsize', type=int, default=1, help='Default stepsize for the transition')
    parser.add_argument('--prewarm', type=int, default=0, help='Number of transitions before starting to record data.')
    parser.add_argument('--revert', type=str2bool, default='true', help='Whether the bot should return to the initial state or not after each step.')
    parser.add_argument('--reset_after_step', type=str2bool, default='false', help='Whether the bot should reset the blackbox after each step.')
    args = parser.parse_args()
    run_bots(args.size, args.num_workers, args.output_folder, args.stepsize, args.prewarm, args.revert, args.reset_after_step)


    
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#