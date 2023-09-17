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

def run_bots(size, num_workers, output_folder, stepsize, prewarm):
    ray.init()
    bots_handler = BotsHandler(size, num_workers, output_folder=output_folder, stepsize=stepsize, prewarm=prewarm)
    bots_handler.collect()
    ray.shutdown()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('--size', type=int, help='Number of transitions to sample')
    parser.add_argument('--num_workers', type=int, help='Number of workers (copies)')
    parser.add_argument('--output_folder', type=str, default='./', help='Output folder')
    parser.add_argument('--stepsize', type=int, default='1', help='Default stepsize for the transition')
    parser.add_argument('--prewarm', type=int, default='0', help='Number of transitions before starting to record data.')
    args = parser.parse_args()
    run_bots(args.size, args.num_workers, args.output_folder, args.stepsize, args.prewarm)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

