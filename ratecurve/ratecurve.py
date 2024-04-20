import pandas as pd
from dateroll import Duration, ddh
from scipy import interpolate

from ratecurve import equations, utils

# Standin for upcoming dateroll features
Duration.just_bds = lambda self, *args, **kwargs: self.just_days
Duration.yf = lambda self, *args, **kwargs: self.just_days / 365


INTERPOLATION_ROOT_DATE = "1/1/2000"

# class InterpResult:
#   TODO
#     .__repr__ class for results of curve fitting.
#     '''
#     def __init__(self,curve,a,b):
#         ...


class Curve:
    """
    Simple and straightforward class for interpolating curves on rates.
    """

    def __init__(
        self,
        d,
        dc="ACT/365",
        cal="ALL",
        method="EXP",
        interp_on="ln(df)",
        interp_method="linear",
        base="t",
    ):
        """
        Parameters
        -----------
        d
            Dict or dict-like raw rate data to construct curve.  Given in form {[tenor/date]:[rate]}.
            Handles dictionary, pd.Series, and 1 dimensional pd.DataFrame
        dc
            Day count convention for calculating accrual. Only "ACT/365" supported for right now.
        cal
            Holiday calendar used in day count calculations. Only "ALL" supported for right now.
        method
            Compounding method for discount and cap factors. Supports 'EXP', 'LIN', and 'YLD'.
        interp_on
            Y-transformation performed on rates before interpolating. Support for 'ln(df)', 'r*t' and 'r'.
        interp_method
            Kind of interpolation performed on data. See scipy.interp1d documentation for details.
        base
            Date at head of curve. Default is current date.
        """
        self.base = ddh(base)  # Base is always in date form
        self.dc = dc
        self.method = method
        self.interp_on = interp_on
        self.cal = cal
        self.interp_method = interp_method
        # Transformations for input and outputs to interpolation
        self.to_x = lambda x: self.make_date_a_number(x)
        self.to_y, self.from_y = self.get_y_transformers(interp_on, method)

        # Data processing and validation will parse and store dates and rates
        if isinstance(d, dict):
            self.dates, self.rates = self.validate_data(d)
        elif isinstance(d, pd.Series):
            data = d.to_dict()
            self.dates, self.rates = self.validate_data(data)
        elif isinstance(d, pd.DataFrame):
            # DataFrame must be either single row or single column arrangable in a tenor:rate format.
            if d.shape[0] > 1 and d.shape[1] > 1:
                raise TypeError(
                    "Data must be dictionary, series, or DataFrame with shape (<=1,<=1)."
                )
            else:
                if utils.isdatelike(d.columns[0]):
                    data = d.T.iloc[:, 0].to_dict()
                    self.dates, self.rates = self.validate_data(data)
                elif utils.isdatelike(d.index[0]):
                    data = d.iloc[:, 0].to_dict()
                    self.dates, self.rates = self.validate_data(data)
                else:
                    raise TypeError("Must have tenor or date-like values.")
        else:
            raise TypeError("Accepted data types are dict, pd.Series and pd.DataFrame.")

        # fit interpolation
        self.fit()

    def validate_data(self, data):
        """
        Validates input data is of type {[date-like]:rate} and returns list of dates and
        a list of rates for interpolation.
        """
        x = []
        y = []
        for i in data.items():
            key = i[0]
            val = i[1]
            try:
                # Convert key to date
                key_as_date = self.to_date(key)
                if not isinstance(val, float):
                    raise
                x.append(key_as_date)
                y.append(val)
            except Exception:
                raise ValueError(
                    "Invalid data. Data must be of form {[date-like object]:float}"
                )
        self.raw_data = data
        return x, y

    def to_date(self, datelike):
        """
        Converts tenors to dates relative to Curve.base date.
        """
        return utils.to_dateroll_date(datelike, self.base)

    def _dt(self, date1, date2):
        """
        Calculates year fraction between 2 dates.
        """
        return utils.delta_t(date1, date2, self.dc, self.cal)

    def _t(self, date):
        """
        Coverts date to year fraction.
        """
        return self._dt(self.base, date)

    def cap_factor(self, date1, date2):
        """
        Interpolated cap factor of curve between two dates. See docs for
        ratecurve.equations.cap_factor for more details.
        """
        # Get interpolated cap factor
        cf01 = self.interpolate_cap_factor(date1)
        cf02 = self.interpolate_cap_factor(date2)

        # Compute forward cap factor
        cf12 = cf02 / cf01
        return cf12

    def disc_factor(self, date1, date2):
        """
        Interpolated discount factor of curve between two dates. See docs for
        ratecurve.equations.disc_factor for more details.
        """
        return 1 / self.cap_factor(date1, date2)

    def get_y_transformers(self, interp_on, method):
        """
        Returns 2 functions:
            1. Convert raw rates into interpolated form
            2. Convert interpolated form to raw_rates
        """

        def to_y(t, rate):
            # From rate to interpolated form
            r = rate
            if interp_on == "r":
                return r
            elif interp_on in ("rt", "r*t"):
                return r * t
            elif interp_on == "ln(df)":
                df = equations.disc_factor(r, t, method)
                return equations.ln(df)
            else:
                raise ValueError(f"Unknown interp_on {interp_on}")

        def from_y(t, y):
            # From interpolated form to cap factor
            if interp_on == "r":
                return equations.cap_factor(y, t, self.method)
            elif interp_on in ("rt", "r*t"):
                return equations.cap_factor(y / t, t, self.method)
            elif interp_on == "ln(df)":
                df = equations.e**y
                return 1 / df

        return to_y, from_y

    def make_date_a_number(self, date):
        """
        Converts date or list of dates to a number(s) for interpolation. Number is
        days since root date (originally set to 1/1/2000).
        """
        return utils.from_date_to_number(
            date, INTERPOLATION_ROOT_DATE, self.dc, self.cal
        )

    def make_number_a_date(self, number):
        """
        Convers interpolation number to date.
        """
        return utils.from_number_to_date(
            number, INTERPOLATION_ROOT_DATE, self.dc, self.cal
        )

    def fit(self):
        """
        Fits interpolation and sets self.f
        """
        dates = self.dates
        rates = self.rates
        x = [self.to_x(date) for date in dates]
        y = [self.to_y(self._t(dates[i]), rates[i]) for i in range(len(self.rates))]
        self.interpolator_unadjusted = interpolate.interp1d(
            x, y, kind=self.interp_method
        )

    def interpolate_cap_factor(self, date):
        """
        Adjusts raw interpolation to return cap factor for given date.
        """
        validated_t = self._t(date)
        x = self.to_x(date)
        unadjusted_interpolation = self.interpolator_unadjusted(x)
        cf = self.from_y(validated_t, unadjusted_interpolation)
        return cf

    def __call__(self, *args):
        """
        Default calls for class instance. curve(a) returns spot discount factor at a.
        curve(a,b) returns forward rate between a and b, where a is convertible to a date before b.
        """
        if len(args) == 1:
            return self.disc_factor(self.base, args[0])
        elif len(args) == 2:
            return self.fwd(args[0], args[1])
        else:
            raise TypeError("Curve instance call takes 1 or 2 positional arguments")

    def fwd(self, date1, date2):
        """
        Computes forward rate between date a and date b.
        """
        cf12 = self.cap_factor(date1, date2)
        dt = self._dt(date1, date2)
        r12 = equations.convert_cap_factor_to_rate(cf12, dt, self.method)
        return r12

    def spot(self, date):
        """
        Computes spot rate at date a. Can return as either rate or discount factor.
        """
        # Convert to dates
        date0 = self.base
        date1 = self.to_date(date)
        # Compute forward rate between b and self.base
        rate = self.fwd(date0, date1)
        return rate
