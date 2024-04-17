import numpy as np
import pandas as pd
from scipy import interpolate
import datetime 
import dateutil

from dateroll import ddh, Date, Duration

# Standin for upcoming dateroll features 
Duration.just_bds = lambda self, *args,**kwargs: self.just_days
Duration.yf = lambda self, *args,**kwargs: self.just_days/365
# Acceptable date-like types
DATE_LIKE_TYPES = (Date,Duration,datetime.datetime,datetime.date,np.datetime64,dateutil.relativedelta.relativedelta,datetime.timedelta,np.timedelta64)
# Shorthand for e, ln
ln = np.log
e = np.e

def disc_factor(r, t, method):
    '''
    The disc_factor is a multiple used to get the present value of a future value. 
    (PV = FV*DiscountFactor) Computed with a given rate, method and time.
    '''
    if method == 'EXP':
        cf = e**(r*t)
    elif method == 'YLD':
        cf = (1+r)**t
    elif method == 'LIN':
        cf = 1+r*t
    else:
        raise ValueError(f'Method {method} unknown')
    df = 1/cf
    return df

def cap_factor(r, t, method):
    '''
    The reciprocal of disc_factor; used to multiply current value to get its
    future value (FV = PV*CapFactor)
    '''
    return 1/disc_factor(r, t, method)

def convert_disc_factor_to_rate(df, t, method):
    '''
    Converts disc_factor to rate for given methods and time for how disc_factor was calculated.
    '''
    cf = 1/df
    if method == 'EXP':
        return ln(cf)/t
    elif method == 'YLD':
        return (cf**(1/t)) - 1
    elif method == 'LIN':
        return (cf-1)/t
    else:
        raise ValueError(f'Method {method} unknown')
    
def convert_cap_factor_to_rate(cf, t, method):
    '''
    Converts cap_factor to rate.
    '''
    df = 1/cf
    return convert_disc_factor_to_rate(df, t, method)


# class InterpResult:
#   TODO    
#     .__repr__ class for results of curve fitting.
#     '''
#     def __init__(self,curve,a,b):
#         ...


class Curve:
    '''
    Simple and straightforward class for interpolating curves on rates.
    '''
    def __init__(self, d, dc='ACT/365',cal='ALL', method='EXP', interp_on='ln(df)', interp_method='linear', base='t'):
        '''
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
            Date at head of curve. Default is today.
        '''
        self.base = ddh(base)  # Base is always in date form
        self.dc = dc 
        self.method = method 
        self.interp_on = interp_on
        self.cal = cal 
        self.interp_method = interp_method
        # Transformations for input and outputs to interpolation
        self.to_x = lambda x: self.make_date_a_number(x,dc,cal)
        self.to_y, self.from_y = self.get_y_transformers(interp_on,method,cal,dc)        

        # Data processing and validation will parse and store dates and rates
        if isinstance(d, dict):
            self.dates, self.rates = self.validate_data(d)
        elif isinstance(d, pd.Series):
            data = d.to_dict()
            self.dates, self.rates = self.validate_data(data)
        elif isinstance(d, pd.DataFrame):
            # DataFrame must be either single row or single column arrangable in a tenor:rate format.
            if d.shape[0] > 1 and d.shape[1] > 1:
                raise TypeError('Data must be dictionary, series, or DataFrame with shape (<=1,<=1).')
            else:
                if self.isdatelike(d.columns[0]):
                    data = d.T.iloc[:,0].to_dict()
                    self.dates, self.rates = self.validate_data(data)
                elif self.isdatelike(d.index[0]):
                    data = d.iloc[:,0].to_dict()
                    self.dates, self.rates = self.validate_data(data)
                else:
                    raise TypeError("Must have tenor or date-like values.")
        else:
            raise TypeError("Accepted data types are dict, pd.Series and pd.DataFrame.")
        
        # fit interpolation
        self.fit()

    def validate_data(self, data):
        '''
        Validates input data is of type {[date-like]:rate} and returns list of dates and 
        a list of rates for interpolation.
        '''
        x = []
        y = []
        for i in data.items():
            key = i[0]
            val = i[1]
            try:
                # Convert key to date
                key_as_date = self.to_dateroll_date(self.to_dateroll_date_like(key))
                if not isinstance(val,float):
                    raise ValueError("Rates must be floats.")
                x.append(key_as_date)
                y.append(val)
            except:
                raise ValueError('Invalid data. Data must be of form {[date-like object]:rate}')
        self.raw_data = data
        return x, y   
    
    def get_y_transformers(self, interp_on, method, cal, dc):
        '''
        Returns 2 functions: 
            1. Convert raw rates into interpolated form 
            2. Convert interpolated form to raw_rates
        '''
        def to_y(date, rate, x):
            # From rate to interpolated form
            r  = rate
            t = (date - self.base).yf(cal, dc)
            if interp_on == 'r':
                return r
            elif interp_on in ('rt','r*t'):
                return r*t
            elif interp_on == 'ln(df)':
                df = disc_factor(r, t, method)
                return ln(df)
            else:
                raise ValueError(f'Unknown interp_on {interp_on}')
            
        def from_y(date, x, y):
            # From interpolated form to rate
            t = (date-self.base).yf(cal, dc)
            if interp_on == 'r':  
                return y
            elif interp_on in ('rt', 'r*t'):
                return y/t
            elif interp_on == 'ln(df)':
                df = e**y
                if df == 1:
                    # Converting discount_factor to rate can result in division by 0 if t = 0
                    return self.rates[0]
                else: 
                    return convert_disc_factor_to_rate(df,t,method)
            
        return to_y, from_y
    

    def isdatelike(self, x):
        '''
        Tests if input is date-like (is or can be converted to dateroll type).
        '''
        if isinstance(x, DATE_LIKE_TYPES):
            return True 
        else:
            if isinstance(x, str):
                try:
                    ddh(x)
                    return True
                except:
                    return False
        return False
    
    def to_dateroll_date_like(self, x):
        '''
        Converts input to dateroll type compatible with Curve class (Date, Duration).
        '''
        if isinstance(x, str):
            # Try to convert string type
            try:
                date = ddh(x) 
                if isinstance(ddh(x), (Date,Duration)):
                    return date
                else:
                    raise TypeError('Must be convertible to dateroll. Date or dateroll.Tenor.')
            except Exception as e:
                raise e
        elif isinstance(x, np.datetime64):
            # Numpy date classes are not directly convertible to dateroll types yet.
            # Can use pandas to convert to datetime which can then be converted to dateroll.
            return ddh(pd.Timestamp(x))
        elif isinstance(x, np.timedelta64):
            return ddh(pd.Timedelta(x))
        elif self.isdatelike(x):
            return ddh(x)
        else:
            raise TypeError
        
    def to_dateroll_date(self, x):
        '''
        Converts input to dateroll.date type relative to self.base date.
        '''
        if isinstance(x, Duration):
            return self.base + x
        elif isinstance(x, Date):
            return x
        else:
            raise TypeError
        

    def  make_date_a_number(self, date, dc, cal):
        '''
        Converts date or list of dates to a number(s) for interpolation. Number is 
        days since 1/1/2000.
        '''
        if isinstance(date, Date):
            if dc.lower().startswith('bd'):
                return (date - '1/1/2000').just_bds(cal=cal, dc=dc) 
            else:
                return (date - '1/1/2000').just_days
        else:  
            # Handles list-like inputs
            try:
                len(date)
                return [self.make_date_a_number(x, dc, cal) for x in date]
            except:
                raise TypeError('Must be Date list-like of Date types to convert to number')
        
    def make_number_a_date(self, number, cal):
        '''
        Convers interpolation number to date.
        '''
        return ddh('1/1/2000') + number

    def fit(self):
        '''
        Fits interpolation and sets self.f
        '''
        dates = self.dates
        rates = self.rates

        x = [self.to_x(date) for date in dates]
        y = [self.to_y(dates[i], rates[i], x[i],) for i in range(len(self.rates))] #self.to_y(self.dates,x,rates)     
        self.f = interpolate.interp1d(x, y, kind=self.interp_method)

    def __call__(self, *args):
        '''
        Default calls for class instance. curve(a) returns spot discount factor at a.
        curve(a,b) returns forward rate between a and b, where a is convertible to a date before b.
        '''
        if len(args)==1:
            return self.spot(args[0], returns='df')
        elif len(args)==2:
            return self.fwd(args[0], args[1])
        else:
            raise TypeError('Curve instance call takes 1 or 2 positional arguments')
 
    def fwd(self, a, b, returns='rate'):
        '''
        Computes forward rate between date a and date b. Can return either rate or discount_factor.
        '''
        # Convert a and b to dates if not already
        a_date = self.to_dateroll_date(self.to_dateroll_date_like(a))
        b_date = self.to_dateroll_date(self.to_dateroll_date_like(b))
        # Convert from date to a number for the interpolated function call
        _a = self.make_date_a_number(a_date, self.dc, self.cal) #should handle cases when tenor is passed for b/a etc.
        _b = self.make_date_a_number(b_date, self.dc, self.cal)
        # Interpolated values
        _ya = self.f(_a)
        _yb = self.f(_b)
        # Spot rates
        spot_a = self.from_y(a_date, _a, _ya)
        spot_b = self.from_y(b_date, _b, _yb)
        #possible times
        t_a = (a_date - self.base).yf(self.cal, self.dc)
        t_b = (b_date - self.base).yf(self.cal, self.dc)
        t_between = (b_date - a_date).yf(self.cal, self.dc)
        # Convert from spot rates to capfactor for forward cap. chain so far is spot->capf ->fwdcapfactor->rate/discountfactor
        cf_a = cap_factor(spot_a, t_a, self.method) # a spot rate
        cf_b = cap_factor(spot_b, t_b, self.method) # b spot rate
        # Forward cap factor calculation
        fwd_cap = cf_b/cf_a
        # Convert fwd_cap back to fwd_rate
        fwd_rate = convert_cap_factor_to_rate(fwd_cap, t_between, self.method)
        
        # Return either rate or discount factor
        if returns in ('rate', 'r'):
            return fwd_rate
        elif returns in('df', 'discount_factor'):
            return disc_factor(fwd_rate, t_a, self.method)
        else:
            raise TypeError('Return must be of type: ["rate", "df"]')

    def spot(self, b, returns='rate') :
        '''
        Computes spot rate at date a. Can return as either rate or discount factor.
        '''
        # Convert to dates
        b_date = self.to_dateroll_date(self.to_dateroll_date_like(b))        
        a_date = self.base  # For spot rates, our a is always our base date
        # Compute forward rate between b and self.base
        rate = self.fwd(a_date, b_date)
        # Time
        t = (b_date - self.base).yf(self.cal, self.dc)
        
        if returns in ('rate', 'r'):
            return rate
        elif returns in ('df','discount_factor'):
            return disc_factor(rate, t, self.method)
        else:
            raise TypeError('Return must be of type: ["rate", "df"]')

