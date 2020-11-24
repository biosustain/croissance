from operator import attrgetter


def score(values, q):
    return (q - min(values)) / (max(values) - min(values)) * 100


def rank_phases(phases, weights, thresholds):
    values = {}
    for attribute in weights:
        values[attribute] = [getattr(phase, attribute) for phase in phases]
        values[attribute].append(thresholds[attribute])

    ranked_phases = []
    for phase in phases:
        rank = sum(
            weight * score(values[attribute], getattr(phase, attribute))
            for attribute, weight in weights.items()
        ) / sum(weights.values())

        ranked_phases.append(phase._replace(rank=rank))

    return sorted(ranked_phases, key=attrgetter("rank"), reverse=True)
