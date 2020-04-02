from math import ceil
import random

from matplotlib import pyplot as plt
import numpy
import parser from tools.parser

args = vars(parser.parse_args())
tests = args['tests']
positives = args['positives']
batch = args['batch']
runs = args['runs']

assert batch >= 0 and tests > 0 and positives > 0, 'what are you doing? stop it!'
assert batch <= tests, 'batch > tests, oof'
assert positives <= tests, 'positives > tests, big oof'

def _chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def chunks(lst, n):
    return list(_chunks(lst, n))

def hasTrue(lst):
    return True if True in lst else False

def countPartitions(partition):
    i = 0
    for p in partition:
        if hasTrue(p):
            i += 1
    return i

truncate = lambda v: ceil(v * 1000) / 1000

def plot(graph, batches, **kwargs):
    print(kwargs, kwargs.values())
    graph.plot(list(kwargs.keys()), list(kwargs.values()), label='Batches ' + str(batches))
    return graph

def compute(batch):
    random.seed()

    negatives = tests - positives

    print('tests:\t\t%s' % tests)
    print('positives:\t%s' % positives)
    perc = 100 / (tests / positives)
    perc_rounded = truncate(perc)
    print('%' + ' positive:\t%s' % perc + '%')
    print('batch:\t\t%s' % batch)

    top_level = ceil(tests / batch)
    print('top_level:\t%s' % top_level)

    print('-----')

    best_case = top_level + (ceil(positives / batch) * batch)
    print('best_case:\t%s' % best_case)

    worst_case = top_level + ((positives if positives < top_level else top_level) * batch)
    print('worst_case:\t%s' % worst_case)

    print('-----')

    # Time to monte carlo!
    tested = []
    for i in range(positives):
        tested.append(True)
    for i in range(negatives):
        tested.append(False)

    def monteCarlo():
        random.shuffle(tested)

        partitioned = chunks(tested, batch)

        # this many partitions have at least one positive test
        count = countPartitions(partitioned)

        return count

    print('Running %s scenarios...' % runs)
    total = 0
    for i in range(runs):
        total += monteCarlo() * batch

    average_run = total / runs
    print('average_run:\t%s' % average_run)
    average_case = top_level + average_run
    print('average_case:\t%s' % average_case)
    assert average_case <= worst_case and average_case >= best_case, 'this should be impossible'
    diff = truncate(tests - average_case)
    if diff > 0:
        print('this setup would SAVE ~%s extra tests' % diff)
    else:
        print('this setup would LOST ~%s more tests' % diff)

    return { 'best_case': best_case, 'worst_case': worst_case, 'average_case': average_case }

if __name__ == '__main__':
    print('test_shortage.py running')
    for b in range(batch - 3, batch + 3):
        plot(plt, b, **compute(b))
    plt.legend()
    plt.suptitle(str(args))
    plt.show()
