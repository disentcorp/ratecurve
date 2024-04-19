import datetime 
import dateutil

from dateroll import ddh, Date, Duration
Duration.just_bds = lambda self, *args,**kwargs: self.just_days
Duration.yf = lambda self, *args,**kwargs: self.just_days/365
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
    
def to_dateroll_date(x, base=None):
    '''
    Converts input tenor to date relative to base if input not date already.
    '''
    # base must be convertable to dateroll.Date if not None
    if base != None:
        try:
            base_date = ddh(base)
            assert isinstance(base_date, Date)
        except:
            TypeError("Base date must be convertable to dateroll.Date")

    # If string, try to convert and recurse on converted value
    if isinstance(x, str):
        
        try:
            date_like = ddh(x) 
            return to_dateroll_date(date_like, base)
        except:
            raise TypeError('Input must be convertible to dateroll.Date or dateroll.Tenor.')
    # If already date-like, convert to dateroll type and convert to date relative to base
    elif isdatelike(x):
        dateroll_obj = ddh(x)  # Converts alternative date types to dateroll.
        if isinstance(dateroll_obj, Date):
            return dateroll_obj
        elif isinstance(dateroll_obj, Duration):
            try:
                return base_date + dateroll_obj
            except:
                # Will fail if no base given
                raise ValueError("Cannot convert tenor without a base date.")
        else:
            raise TypeError("Unconvertible date-type.")        
    else:
        raise TypeError('Unrecognized date-type for conversion')
    
def from_date_to_number(date, root, dc, cal):
    '''
    Converts date or list of dates to a number(s) for interpolation. Number is 
    days since root date.
    '''
    validated_root = to_dateroll_date(root)
    validated_date = to_dateroll_date(date,validated_root)
    if isinstance(date, Date):
        if dc.lower().startswith('bd'):
            return (validated_date - validated_root).just_bds(cal=cal, dc=dc) 
        else:
            return (validated_date - validated_root).just_days
    else:
        raise TypeError("Can only convert date-like types to number.")

def from_number_to_date(number, root, dc, cal):
    '''
    Convers interpolation number to date.
    '''
    validated_root = to_dateroll_date(root)
    return validated_root + number  #TODO properly invert from_date_to_number given dc and cal

def delta_t(date1, date2, dc, cal):
    '''
    Calculate year fraction between two dates (date2 after date1)
    '''
    # Validate and convert to appropriate dates
    validated_date1 = to_dateroll_date(date1)
    validated_date2 = to_dateroll_date(date2)
    return (validated_date2 - validated_date1).yf(cal, dc)
