import pandas


class TSVReader:
    def __init__(self, filepath):
        self._filepath = filepath

    def read(self):
        with open(self._filepath, "rt") as handle:
            data = pandas.read_csv(handle, sep="\t", header=0, index_col=0)

        return [(name, data[name].dropna()) for name in data.columns]

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass
