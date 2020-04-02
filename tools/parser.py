import argparse
from operator import itemgetter

parser = argparse.ArgumentParser(description='Test batched testing approaches.')
parser.add_argument('tests', default=100, type=int, nargs='?')
parser.add_argument('positives', default=19, type=int, nargs='?')
parser.add_argument('batch', default=5, type=int, nargs='?')
parser.add_argument('runs', default=500, type=int, nargs='?')

args = parser.parse_args()
args = vars(args)

tests, positives, batch, runs = itemgetter('tests', 'positives', 'batch', 'runs')(args)

assert batch >= 0 and tests > 0 and positives > 0, 'what are you doing? stop it!'
assert batch <= tests, 'batch > tests, oof'
assert positives <= tests, 'positives > tests, big oof'
