import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Test batched testing approaches.')
parser.add_argument('--test_executions', default=100, type=int, nargs='?', dest='test_executions')
# Maine CDC April 15th 2020 confirmed test cases over negative result cases:
# 770 / 14076 = 0.05470304063
parser.add_argument('--positives', default=5, type=int, nargs='?', dest='positives')
# TODO add logic to pass a % (and logic to floor it, probably, and not rounding it)
parser.add_argument('--batch', default=5, type=int, nargs='?', dest='batch')
parser.add_argument('--runs', default=400, type=int, nargs='?', dest='runs')
parser.add_argument('--run_type', default='csv', type=str, nargs='?', choices=['csv', 'plot'], dest='run_type')
parser.add_argument('--csv_full', default=False, action='store_true', dest='csv_full')

args = parser.parse_args()
args = vars(args)

test_executions, positives, batch, runs, run_type, csv_full = itemgetter('test_executions', 'positives', 'batch', 'runs', 'run_type', 'csv_full')(args)

assert batch >= 0 and test_executions > 0 and positives > 0, 'what are you doing? stop it!'
assert batch <= test_executions, 'batch > tests, oof'
assert positives <= test_executions, 'positives > tests, big oof'
