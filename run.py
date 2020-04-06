from math import ceil
import random

from tools.parser import \
    args, \
    test_executions, \
    positives, \
    batch, \
    runs, \
    run_type

CSV_FILENAME = 'batch_tests.csv'
BATCH_RANGE = 6


def chunks(input, n):
    """Return a list of lists from input, each of <n> length."""
    def _chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
            
    return list(_chunks(input, n))


# TODO what are better performance choices for here?
def countPartitions(partition):
    hasTrue = lambda lst: True if True in lst else False

    i = 0
    for p in partition:
        if hasTrue(p):
            i += 1
    return i

truncate = lambda v: ceil(v * 1000) / 1000

def plot(graph, **kwargs):
    print('plot', kwargs)
    label = 'Batches of size ' + str(kwargs.get('batch_size'))
    graph.plot(list(kwargs.keys()), list(kwargs.values()), label=label)
    return graph

def compute(batch):
    random.seed()

    negatives = test_executions - positives

    # TODO convert print statements to logger format
    print('test_executions/tests:\t\t%s' % test_executions)
    print('positives:\t%s' % positives)
    perc = 100 / (test_executions / positives)
    perc_rounded = truncate(perc)
    print('%' + ' positive:\t%s' % perc + '%')
    print('batch:\t\t%s' % batch)

    top_level = ceil(test_executions / batch)
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

    def monteCarloes():
        for i in range(runs):
            yield monteCarlo() * batch

    all_runs = list(monteCarloes())
    
    def summation(li):
        sum = 0
        for v in li:
            sum += v
        return sum

    total_tests_used = summation(all_runs)
    print('total_tests_used:\t', total_tests_used)
    average_run = total_tests_used / runs
    print('average_run:\t%s' % average_run)
    average_case = top_level + average_run
    print('average_case:\t%s' % average_case)
    assert average_case <= worst_case and average_case >= best_case, 'this should be impossible'
    diff = truncate(test_executions - average_case)
    if diff > 0:
        print('this setup would SAVE ~%s extra tests' % diff)
    else:
        print('this setup would LOST ~%s more tests' % diff)

    return { 
        'batch_size': batch,
        'test_executions': test_executions,
        'positives': positives,
        'negatives': negatives,
        'best_case': best_case, 
        'worst_case': worst_case, 
        'average_case': average_case,
        'total_tests_used': total_tests_used,
        'tests_minus_average': test_executions - average_case,
        'runs': runs,
    }


def run():
    if run_type == 'plot':
        run_plot()
    elif run_type == 'csv':
        run_csv()
    else:
        print('error: run_type invalid.\t', run_type)
 

def run_plot():
    from matplotlib import pyplot as plt
    import numpy
    for b in range(batch - BATCH_RANGE, batch + BATCH_RANGE):
        if b > 0:
            plot(plt, **compute(b))
        else:
            print('b was too low:\t', b)
    plt.legend()
    plt.suptitle(str(args))
    plt.show()

def run_csv():
    import csv # https://docs.python.org/3/library/csv.html#csv.writer
    with open(CSV_FILENAME, 'w', newline='') as csvfile:
        # TODO centralize keywords
        fieldnames = [
            'batch_size',
            'test_executions',
            'positives',
            'negatives',
            'best_case', 
            'worst_case', 
            'average_case',
            'total_tests_used',
            'tests_minus_average',
            'runs',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for b in range(batch - BATCH_RANGE, batch + BATCH_RANGE):
            if b > 0:
                writer.writerow(compute(b))
            else:
                print('b was too low:\t', b)
    print(CSV_FILENAME + ' created.')

if __name__ == '__main__':
    print('test_shortage.py running')
    run()
