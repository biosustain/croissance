import csv

from croissance.estimation import GrowthPhase, AnnotatedGrowthCurve


class TSVWriter:
    def __init__(self, filepath, exclude_default_phase: bool = True):
        self._exclude_default_phase = exclude_default_phase
        self._handle = open(filepath, "wt")
        self._writer = csv.writer(
            self._handle, delimiter="\t", quoting=csv.QUOTE_MINIMAL
        )

        self._writer.writerow(
            ["name", "phase", "slope", "intercept", "N0", "SNR", "rank"]
        )

    def write(self, name: str, curve: AnnotatedGrowthCurve):
        if not self._exclude_default_phase:
            phase = GrowthPhase.pick_best(curve.growth_phases, "rank")

            if not phase:
                self._writer.writerow([name, 0, None, None, None])
            else:
                self._writer.writerow(
                    [
                        name,
                        0,
                        phase.slope,
                        phase.intercept,
                        phase.n0,
                        phase.SNR,
                        phase.rank,
                    ]
                )

        for i, phase in enumerate(curve.growth_phases, start=1):
            self._writer.writerow(
                [name, i, phase.slope, phase.intercept, phase.n0, phase.SNR, phase.rank]
            )

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        self._handle.close()
