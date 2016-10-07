from operator import itemgetter

import numpy


def score(values, q):
    return (q - numpy.min(values)) / (numpy.max(values) - numpy.min(values)) * 100


def rank_phases(phases, weights, thresholds):
    values = {}
    scores = []

    for attribute, weight in weights.items():
        values[attribute] = [getattr(phase, attribute) for phase in phases]

    for phase in phases:
        scores.append((sum(weight * score([thresholds[attribute]] + values[attribute], getattr(phase, attribute))
                           for attribute, weight in weights.items()) / sum(weights.values()),
                       phase))

    ranked_phases = []
    for rank, phase in sorted(scores, key=itemgetter(0), reverse=True):
        phase.attributes['rank'] = rank
        ranked_phases.append(phase)

    return ranked_phases
