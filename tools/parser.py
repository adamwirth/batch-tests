import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Test batched testing approaches.')
parser.add_argument('--test_executions', default=100, type=int, nargs='?', dest='test_executions')
parser.add_argument('--positives', default=19, type=int, nargs='?', dest='positives')
parser.add_argument('--batch', default=5, type=int, nargs='?', dest='batch')
parser.add_argument('--runs', default=500, type=int, nargs='?', dest='runs')
parser.add_argument('--run_type', default='csv', type=str, nargs='?', choices=['csv', 'plot'], dest='run_type')

args = parser.parse_args()
args = vars(args)

test_executions, positives, batch, runs, run_type = itemgetter('test_executions', 'positives', 'batch', 'runs', 'run_type')(args)

assert batch >= 0 and test_executions > 0 and positives > 0, 'what are you doing? stop it!'
assert batch <= test_executions, 'batch > tests, oof'
assert positives <= test_executions, 'positives > tests, big oof'
