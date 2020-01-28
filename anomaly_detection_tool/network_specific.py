def domain_analyze(results):
    for pos, x in zip(range(len(results)), results):
        if (pos == 0 or pos == 1) and x[0] == 9999:
            results[pos] = (0, 0)
        elif pos == 0 or pos == 1:
            results[pos] = (results[pos][0], results[pos][1])
    return results
