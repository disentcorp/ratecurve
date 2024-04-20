import numpy as np

# Shorthand for e, ln
ln = np.log
e = np.e


def cap_factor(r, t, method):
    """
    The disc_factor is a multiple used to get the present value of a future value.
    (PV = FV*DiscountFactor) Computed with a given rate, method and time.
    """
    if method == "EXP":
        cf = e ** (r * t)
    elif method == "YLD":
        cf = (1 + r) ** t
    elif method == "LIN":
        cf = 1 + r * t
    else:
        raise ValueError(f"Method {method} unknown")
    return cf


def disc_factor(r, t, method):
    """
    The reciprocal of disc_factor; used to multiply current value to get its
    future value (FV = PV*CapFactor)
    """
    return 1 / cap_factor(r, t, method)


def convert_cap_factor_to_rate(cf, t, method):
    """
    Converts cap_factor to rate.
    """
    if method == "EXP":
        r = ln(cf) / t
    elif method == "YLD":
        r = (cf ** (1 / t)) - 1
    elif method == "LIN":
        r = (cf - 1) / t
    else:
        raise ValueError(f"Method {method} unknown")
    return r


def convert_disc_factor_to_rate(df, t, method):
    """
    Converts disc_factor to rate for given methods and time for how disc_factor was calculated.
    """
    cf = 1 / df
    return convert_cap_factor_to_rate(cf, t, method)
