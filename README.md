# `simplecurve`

**`simplecurve`** is the no-nonsense curve interpolation library.
<br />
```
$ pip install ratecurve
```
## Quick Start:
```python
curve_data =  {
    "0d":.053,    
    "1m":.0548,
     "6m":.0538,
     "1y":.0517,
     "2y":.0493,
     "10y":.0456,
     "20y":.0477,
     "30y":.0465
     }  # Start with a dictionary of pillars and rates 
curve = Curve(curve_data)
```
```python
>>> curve("1/1/2025")  # Calling on single date or tenor will give spot discount factor
0.9640427167805141
>>> curve("1/1/2025", "4/1/2025")  # Calling on 2 dates or tenors will give fwd rate between two dates
0.049588461538461984
>>> curve.fwd("1/1/2025", "4/1/2025")  # Forward rate function accepts two dates, or date and tenor. Tenor is calculated after first date.
0.049588461538461984
>>> curve.spot("3m")  # Spot rate function accepts date or tenor
0.05399823313940969
>>> curve.disc_factor("1/1/2025", "4/1/2025")  # Computes forward discount factor
0.9878471576993672
>>> curve.cap_factor("1/1/2025", "4/1/2025")  # Computes forward cap factor
1.0123023508301994
```
## Curve Parameters
```python
Curve(  
        d,
        dc="ACT/365",
        cal="ALL",
        method="EXP",
        interp_on="ln(df)",
        interp_method="linear",
        base="t"
        )
```




| param_name | description| default | 
| ---------- | ------| -------------| 
| d          | Dict or dict-like raw rate data to construct curve. Handles dictionary, pd.Series and 1 dimensional pd.DataFrame       | N/A
| dc          |               Day count convention for calculating accrual. Only "ACT/365" supported for right now. | "ACT/365"
| cal          |               Holiday calendar used in day count calculations. Only "ALL" supported for right now. | "ALL"
| method          |             Compounding method for discount and cap factors. Supports 'EXP', 'LIN', and 'YLD'. | "EXP"
| interp_on          |             Y-transformation performed on rates before interpolating. Support for 'ln(df)', 'r*t' and 'r'. | "ln(df)"
| interp_method          |             Kind of interpolation performed on data. See scipy.interp1d documentation for details. | "linear"
| base          |             Date at head of curve. Default is current date. | "t"




Happy interpolating! 
\- The Disent Team
