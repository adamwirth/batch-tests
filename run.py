from math import ceil
import random

from tools.parser import \
    args, \
    test_executions, \
    positives, \
    batch, \
    runs, \
    run_type, \
    csv_full

CSV_FILENAME = 'batch_tests.csv'
BATCH_RANGE = 6
POSITIVES_RANGE = 3


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

def compute(batch, positives=positives):
    random.seed()

    # TODO convert print statements to logger format
    
    negatives = test_executions - positives
    perc = 100 / (test_executions / positives)
    print('test_executions/tests:\t\t%s' % test_executions)
    print('positives:\t%s' % positives)
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
        'percentage_positive': perc,
        'best_case': best_case, 
        'worst_case': worst_case, 
        'average_case': average_case,
        'total_tests_used': total_tests_used,
        'tests_minus_average': test_executions - average_case,
        'runs': runs,
        'all_runs': all_runs,
    }

def batch_size_of_one(positives=positives):
    return {
        'batch_size': 1,
        'test_executions': test_executions,
        'positives': positives,
        'negatives': test_executions - positives,
        'percentage_positive': 100 / (test_executions / positives),
        'best_case': 100, 
        'worst_case': 100, 
        'average_case': 100,
        'total_tests_used': 100,
        'tests_minus_average': 0,
        'runs': runs,
        'all_runs': [100] * runs,
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
            'runs',
            'test_executions',
            'positives',
            'negatives',
            'percentage_positive',
            'total_tests_used',
            'best_case', 
            'worst_case',
        ]
        if csv_full:
            fieldnames.append('individual_run')
        else:
            fieldnames.append('average_case')
            fieldnames.append('tests_minus_average')

        print('fieldnames', fieldnames)

        def omit(d, keys):
           return {x: d[x] for x in d if x not in keys}

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for b in range(batch - BATCH_RANGE, batch + BATCH_RANGE):
            
            if b >= 1:
                for posivs in range(positives - POSITIVES_RANGE, positives + POSITIVES_RANGE):
                    
                    if posivs > 1:
                        computation = compute(b, positives=posivs) if b > 1 else batch_size_of_one(positives=posivs)
                        if csv_full:
                            all_runs = computation['all_runs']
                            computation = omit(computation, ['average_case', 'tests_minus_average', 'all_runs'])
                            for run in all_runs:
                                computation['individual_run'] = run
                                writer.writerow(computation)
                        else:
                            computation = omit(computation, ['all_runs'])
                            writer.writerow(computation)
                    else:
                        print('posivs was too low (<=1):\t', posivs)
            else:
                print('b was too low (<1):\t', b)
    print(CSV_FILENAME + ' created.')

if __name__ == '__main__':
    print('test_shortage.py running')
    run()
