import pandas


class TSVReader(object):

    def read(self, file):
        data = pandas.read_csv(file,
                               sep="\t",
                               header=0,
                               index_col=0)

        names = data.columns

        for name in names:
            curve = data[name].dropna()
            yield name, curve
