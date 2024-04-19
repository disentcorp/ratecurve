import datetime 
import dateutil

from dateroll import ddh, Date, Duration

# Acceptable date-like types
DATE_LIKE_TYPES = (Date,Duration,datetime.datetime,datetime.date,dateutil.relativedelta.relativedelta,datetime.timedelta)

def isdatelike(x):
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
    
def to_dateroll_date(x, base):
    '''
    Converts input tenor to date relative to base if input not date already.
    '''
    # base must be convertable to dateroll.Date
    try:
        base_date = ddh(base)
        assert isinstance(base_date, Date)
    except:
        TypeError("Base date must be convertable to dateroll.Date")

    if isinstance(x, str):
        # Try to convert string type
        try:
            date_like = ddh(x) 
            return to_dateroll_date(date_like, base_date)
        except:
            raise TypeError('Input must be convertible to dateroll.Date or dateroll.Tenor.')
    elif isdatelike(x):
        dateroll_obj = ddh(x)
        if isinstance(dateroll_obj, Date):
            return dateroll_obj
        elif isinstance(dateroll_obj, Duration):
            return base_date + dateroll_obj
        else:
            raise TypeError("Unconvertible date-type.")        
    else:
        raise TypeError('Unrecognized date-type for conversion')
        