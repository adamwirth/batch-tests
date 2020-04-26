from math import ceil
import random
import logging

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


def countPartitions(partition):
    i = 0
    for p in partition:
        if True if True in p else False:
            i += 1
    logging.debug('countPartitions: %s', i)
    return i

truncate = lambda v: ceil(v * 1000) / 1000

def plot(graph, **kwargs):
    logging.debug('plot; %s', kwargs)
    label = 'Batches of size ' + str(kwargs.get('batch_size'))
    graph.plot(list(kwargs.keys()), list(kwargs.values()), label=label)
    return graph

def compute(batch, positives=positives):
    random.seed()
    
    negatives = test_executions - positives
    perc = 100 / (test_executions / positives)
    logging.debug('test_executions/tests:\t%s', test_executions)
    logging.debug('positives:\t%s', positives)
    logging.debug('percentage that are positive:\t%s', perc)
    logging.debug('batch:\t\t%s', batch)

    top_level = ceil(test_executions / batch)
    logging.debug('top_level:\t%s', top_level)

    logging.debug('-----')

    best_case = top_level + (ceil(positives / batch) * batch)
    logging.debug('best_case:\t%s', best_case)

    worst_case = top_level + ((positives if positives < top_level else top_level) * batch)
    logging.debug('worst_case:\t%s', worst_case)

    logging.debug('-----')

    # Time to monte carlo!
    tested = []
    for i in range(positives):
        tested.append(True)
    for i in range(negatives):
        tested.append(False)

    def monteCarlo():
        random.shuffle(tested)

        partitioned = chunks(tested, batch)

        logging.debug('partitioned; %s', partitioned)

        # this many partitions have at least one positive test
        count = countPartitions(partitioned)

        return count

    logging.debug('Running %s scenarios...', runs)

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
    logging.debug('total_tests_used:\t', total_tests_used)
    average_run = total_tests_used / runs
    logging.debug('average_run:\t%s', average_run)
    average_case = top_level + average_run
    logging.debug('average_case:\t%s', average_case)
    assert average_case <= worst_case and average_case >= best_case, 'this should be impossible'
    diff = truncate(test_executions - average_case)
    if diff > 0:
        logging.debug('this setup would SAVE ~%s extra tests', diff)
    else:
        logging.debug('this setup would LOST ~%s more tests', diff)

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
        logging.error('run_type invalid.\t%s', run_type)
 

def run_plot():
    from matplotlib import pyplot as plt
    import numpy
    for b in range(batch - BATCH_RANGE, batch + BATCH_RANGE):
        if b > 0:
            plot(plt, **compute(b))
        else:
            logging.debug('batch value "b" was too low:\t%s', b)
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

        logging.debug('fieldnames:\t%s', fieldnames)

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
                        logging.debug('posivs value was too low (<=1):\t%s', posivs)
            else:
                logging.debug('batch_size value "b" was too low (<1):\t%s', b)
    logging.info('%s created.', CSV_FILENAME)

if __name__ == '__main__':
    logging.debug('run.py running')
    run()
