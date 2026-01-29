# %% [markdown]
# # Croissance Tutorial
#
# Examples taken from unit tests of the package.

# %%
import numpy as np
import pandas as pd

import croissance
from croissance import plot_processed_curve, process_curve

croissance.__version__

yscale = "both" # 'linear', 'log', 'both'

# %%
mu = 0.5
pph = 4.0
curve = pd.Series(
    data=[np.exp(mu * i / pph) for i in range(100)],
    index=[i / pph for i in range(100)],
)

result = croissance.process_curve(curve, constrain_n0=True, n0=0.0)
plot_processed_curve(result, yscale=yscale)
result

# %%
result = process_curve(curve, constrain_n0=False)
plot_processed_curve(result, yscale=yscale)
result

# %%
mu = 0.5
pph = 4.0

curve = pd.Series(
    data=(
        [1.0] * 5
        + [np.exp(mu * i / pph) for i in range(25)]
        + [np.exp(mu * 24 / pph)] * 20
    ),
    index=([i / pph for i in range(50)]),
)

result = process_curve(curve, constrain_n0=True, n0=0.0)
plot_processed_curve(result, yscale=yscale)
result

# %%
result = process_curve(curve, constrain_n0=False)
plot_processed_curve(result, yscale=yscale)
result


# %%
mu = 0.20
pph = 4.0

curve = pd.Series(
    data=(
        [i / 10.0 for i in range(10)]
        + [np.exp(mu * i / pph) for i in range(25)]
        + [np.exp(mu * 24 / pph)] * 15
    ),
    index=([i / pph for i in range(50)]),
)
result = process_curve(curve, constrain_n0=True, n0=0.0)
plot_processed_curve(result, yscale=yscale)
result


# %%
result = process_curve(curve, constrain_n0=False)
plot_processed_curve(result, yscale=yscale)
result

# %% [markdown]
# The end.
