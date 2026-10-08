"""A (too) simple implementation of the block averaging method.

`num_independent` estimates the number of independent samples in a time-correlated sequence.
It is written for educational purposes and should not be trusted for production simulations.
"""

import matplotlib.pyplot as plt
import numpy as np

__all__ = ("averror", "num_independent")


def averror(values, num=None):
    """Compute the error on the average of (un)correlated samples.

    Parameters
    ----------
    values
        samples for which the error on the average is computed.
    num
        The number of independent samples.
        When not given, the default is len(values),
        which would be correct for uncorrelated samples.

    Returns
    -------
    averror
        The error on the averge.

    """
    if num is None:
        num = len(values)
    elif num <= 1:
        return np.nan
    return np.std(values) / np.sqrt(num - 1)


def num_independent(values, fignum=None):
    """Estimate the number of independent samples in a time series.

    This implementation of the block averaging method
    is based on the description in the book of Allen and Tildesley.
    In addition to the book, this code attempts to safeguard against ballistic motion artifacts
    when performing the extrapolation towards infinite block sizes.

    Parameters
    ----------
    values
        A time-correlated series, must be a numpy array with shape (N,).
    fignum
        A matplotlib figure number for plotting the inefficiency and the
        model used for extrapolation.

    Returns
    -------
    indep
        The number of independent samples. When a constant input is provided,
        or in a few pathological cases, the result will be 1.
    quality
        An empirical quality indicator to judge if the series is sufficiently
        long for a reliable estimate of the number of independent samples.
        This should be at least 5, preferrably more. When less than 5,
        the time series should be made at least 2**(5-quality) times longer.

    """
    if values.ndim != 1:
        raise TypeError("Only one-dimensional arrays are supported.")

    # At least 16 blocks, then halve size at each iteration.
    bss = []
    ineffs = []
    bs = len(values) // 16
    while bs >= 1:
        nb = len(values) // bs
        blocks = values[: nb * bs].reshape(nb, bs)
        avvar = blocks.mean(axis=1).var(ddof=1) / (nb - 1)
        bss.insert(0, bs)
        ineffs.insert(0, avvar)
        bs //= 2

    # Return in case of no blocks
    if len(bss) < 1:
        return 1, 0

    # Convert to inefficiencies.
    bss = np.array(bss)
    ineffs = np.array(ineffs)
    ineffs /= ineffs[0]

    # Fit a simple model:  y = a * x / (a + x - 1)
    # Discard decreasing part of the inefficiency, e.g. due to ballistic motion.
    i0 = ineffs.argmin()
    y = ineffs[i0:] / ineffs[i0]
    x = bss[i0:] / bss[i0]
    # At least two data points are needed for the fit.
    if len(y) >= 2:
        dm = (y - x) / x
        ev = (y * (1 - x)) / x
        a = np.dot(ev, dm) / np.dot(dm, dm)
        ineff_limit = a * ineffs[i0]
        optbs = a * bss[i0]
        ineffs_model = ineff_limit * x / (a + x - 1)
    else:
        ineff_limit = 0
        optbs = len(values)
        ineffs_model = None

    if ineff_limit <= 0 or ineff_limit > len(values):
        num_indep = 1
    else:
        num_indep = len(values) / ineff_limit

    # The quality measure is the minimum of the number of points
    # used in the fit and the number of points after the optimal
    # block size.
    quality = min(len(y), (bss > optbs).sum())

    if fignum is not None:
        plt.close(fignum)
        _fig, ax = plt.subplots(num=fignum)
        ax.set_title(
            f"Statistical inefficiency: {ineff_limit:.1f} ||"
            f"Independent samples: {num_indep:.1f} ||"
            f"Quality: {quality:d}"
        )
        ax.plot(bss, ineffs, "o", color="#aaaaaa")
        ax.plot(bss[i0:], ineffs[i0:], "ko")
        if ineffs_model is not None:
            ax.plot(bss[i0:], ineffs_model, "-", color="C0")
            ax.axhline(ineff_limit, color="C0", ls=":")
            ax.axvline(optbs, color="C0", ls=":")
        ax.set_xscale("log")
        ax.set_xlabel("Block size")
        ax.set_ylabel("Statistical inefficiency")

    return num_indep, quality
