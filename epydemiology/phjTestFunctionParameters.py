import pkg_resources

try:
    pkg_resources.get_distribution('numpy')
except pkg_resources.DistributionNotFound:
    numpyPresent = False
    print("Error: Numpy package not available.")
else:
    numpyPresent = True
    import numpy as np


try:
    pkg_resources.get_distribution('pandas')
except pkg_resources.DistributionNotFound:
    pandasPresent = False
    print("Error: Pandas package not available.")
else:
    pandasPresent = True
    import pandas as pd


import collections
import inspect



# This is an attempt to standardise the returns from assert() function.
# phjArgName is a string giving the name of function argument.
# phjArgValue is the argument.
# phjType is the type that the variable must take. Can pass a tuple of types for multiple options.
# phjBespokeMessage is a message displayed in the event of an AssertionException instead of the generic message.
# phjMustBePresentColumnList is a string or a list of column names of which phjArgValue must be one.
# phjMustBeAbsentColumnList is a string or a list of column names in which phjArgValue must not be included.
# phjAllowedOptions can be a list or a dict containing 'min' and 'max' keys.
def phjAssert(phjArgName,
              phjArgValue,
              phjType,
              phjBespokeMessage = None,
              phjMustBePresentColumnList = None,
              phjMustBeAbsentColumnList = None,
              phjAllowedOptions = None):
    
    # Define names for classes
    phjClassNames = {"<class 'str'>":'string',
                     "<class 'float'>": 'float',
                     "<class 'int'>": 'integer',
                     "<class 'bool'>": 'boolean',
                     "<class 'list'>": 'list',
                     "<class 'tuple'>": 'tuple',
                     "<class 'dict'>": 'dictionary',
                     "<class 'collections.OrderedDict'>": 'dictionary',
                     "<class 'collections.UserDict'>": 'dictionary',
                     "<class 'collections.abc.Mapping'>": 'dictionary',
                     "<class 'pandas.core.frame.DataFrame'>": 'Pandas dataframe'}

    # Construct generic message regarding permissable types. For example, if phjType
    # is a single value (e.g. str) then the message in the event of assert being False
    # would need to indicate that the type should be a 'string'. If phjType is a tuple
    # of potential values (e.g. (str,int,float,list)) then the message in the event of
    # assert being False would need to indicate that the required types should be
    # 'string, integer, float or list'.
    if isinstance(phjType,tuple):
        
        if len(phjType) >= 2:
            # List of unique names of types
            phjUniqueClassNames = list(set([phjClassNames[str(i)] for i in phjType]))
            
            phjMessageSuffix = '{} or {}'.format(', '.join(phjUniqueClassNames[:-1]),
                                                           phjUniqueClassNames[-1])
            
        else:
            phjMessageSuffix = phjClassNames[str(phjType[0])]
    
    else:
        phjMessageSuffix = phjClassNames[str(phjType)]
    
    
    try:
        # Check that 
        if isinstance(phjArgValue,(str,float,int,bool)):
            
            if phjBespokeMessage is None:
                assert isinstance(phjArgValue,phjType),"Argument '{0}' ('{1}') needs to be a {2}.".format(phjArgName,
                                                                                                          phjArgValue,
                                                                                                          phjMessageSuffix)
            
            else:
                assert isinstance(phjArgValue,phjType),phjBespokeMessage
                
        else:
            
            if phjBespokeMessage is None:
                assert isinstance(phjArgValue,phjType),"Argument '{0}' needs to be a {1}.".format(phjArgName,
                                                                                                  phjMessageSuffix)
            
            else:
                assert isinstance(phjArgValue,phjType),phjBespokeMessage
        
        
        # Depending on the type of passed variable phjArgValue, check that value lies
        # within correct limits.
        if isinstance(phjArgValue,str):
            
            # If phjMustBePresentColumnList parameter is set then check that phjArgValue is
            # indeed present in that list (e.g. list of dataframe column names).
            if phjMustBePresentColumnList is not None:
                
                # If phjMustBePresentColumnList is a list, then check that phjArgValue is included
                if isinstance(phjMustBePresentColumnList,list):
                    assert phjArgValue in phjMustBePresentColumnList,"Variable '{0}' ('{1}') is not present in list of columns.".format(phjArgName,phjArgValue)
                
                # phjMustBePresentColumnList may be a single string
                elif isinstance(phjMustBePresentColumnList,str):
                    assert phjArgValue == phjMustBePresentColumnList,"Variable '{0}' ('{1}') must be '{2}'.".format(phjArgName,phjArgValue,phjMustBePresentColumnList)
            
            # If phjMustBeAbsentColumnList parameter is set then check that phjArgValue is
            # not present in that list (e.g. list of dataframe column names).
            if phjMustBeAbsentColumnList is not None:
                
                # If phjMustBeAbsentColumnList is a list, then check that phjArgValue is NOT included
                if isinstance(phjMustBeAbsentColumnList,list):
                    assert phjArgValue not in phjMustBeAbsentColumnList,"Variable '{}' already exists in the list of columns.".format(phjArgValue)
                
                # phjMustBeAbsentColumnList may be a single string
                elif isinstance(phjMustBeAbsentColumnList,str):
                    assert phjArgValue == phjMustBeAbsentColumnList,"Variable '{}' must NOT be '{}'.".format(phjArgValue,phjMustBeAbsentColumnList1)
            
            if phjAllowedOptions is not None:
                # Cannot think of any reasons why allowed options would be a single value.
                # Therefore, the phjArgValue must be one of values included in list.
                if isinstance(phjAllowedOptions,list):
                    # If is a string then assert if string contained in list:
                    assert phjArgValue in phjAllowedOptions, "Parameter '{0}' ('{1}') is not an allowed value.".format(phjArgName,phjArgValue)
                
                
        # If phjArgValue is an int or a float then check that it is an allowed value in
        # the phjAllowedOptions list or is in range as set by the min and max values in
        # phjAllowedOptions dict.
        elif isinstance(phjArgValue,(int,float)):
            
            if phjAllowedOptions is not None:
                # Cannot think of any reasons why allowed options would be a single value.
                # Therefore, the phjArgValue must be one of values included in list or a
                # value that lies in a range.
                if isinstance(phjAllowedOptions,list):
                    assert phjArgValue in phjAllowedOptions, "Parameter '{0}' ('{1}') is not an allowed value.".format(phjArgName,phjArgValue)
            
                elif isinstance(phjAllowedOptions,collections.abc.Mapping): # collections.Mapping will work for dict(),
                                                                            # collections.OrderedDict() and collections.UserDict()
                                                                            # (see comment by Alexander Ryzhov at
                                                                            # https://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python).
                                                                            # Also, another comment says that collections.Mapping and collections.abc.Mapping
                                                                            # are the same but collections.abc is not available before Python 3.3. Also,
                                                                            # collections.Mapping, whilst still available in Python 3.6, is not documented.
                    # Compare keys in dictionary with allowed keys. Using collections.Counter() will allow a comparison
                    # where duplicates are NOT removed (as with set() ) but order is not important
                    # (see: https://stackoverflow.com/questions/9623114/check-if-two-unordered-lists-are-equal)
                    if collections.Counter([k for k,v in phjAllowedOptions.items()]) == collections.Counter(['min','max']):
                        assert (phjArgValue >= phjAllowedOptions['min']) & (phjArgValue <= phjAllowedOptions['max']), "Parameter '{0}' ('{1}') is outside the allowed range ({2} to {3}).".format(phjArgName,
                                                                                                                                                                                                  phjArgValue,
                                                                                                                                                                                                  phjAllowedOptions['min'],
                                                                                                                                                                                                  phjAllowedOptions['max'])
                    
                    elif collections.Counter([k for k,v in phjAllowedOptions.items()]) == collections.Counter(['min']):
                        assert (phjArgValue >= phjAllowedOptions['min']), "Parameter '{0}' ('{1}') is less than the allowed minimum value ({2}).".format(phjArgName,
                                                                                                                                                         phjArgValue,
                                                                                                                                                         phjAllowedOptions['min'])
                    
                    elif collections.Counter([k for k,v in phjAllowedOptions.items()]) == collections.Counter(['max']):
                        assert (phjArgValue <= phjAllowedOptions['max']), "Parameter '{0}' ('{1}') is greater than the allowed maximum value ({2}).".format(phjArgName,
                                                                                                                                                            phjArgValue,
                                                                                                                                                            phjAllowedOptions['max'])
        
        # If the phjArgValue is a list then check that all the items are all included
        # in the list of allowed options.
        # Potentially, could use collections.abc.Sequence instead of list to allow any
        # sequence type to be included (see: https://stackoverflow.com/questions/35690572/what-does-isinstance-with-a-dictionary-and-abc-mapping-from-collections-doing)
        elif isinstance(phjArgValue,list):
        
            if phjMustBePresentColumnList is not None:
            
                if isinstance(phjMustBePresentColumnList,list):
                    
                    # Check that all items in phjArgValue list are contained in the
                    # phjMustBePresentColumnList.
                    assert set(phjArgValue).issubset(phjMustBePresentColumnList), "The elements in '{0}' ('{1}') do not all exist in list of columns.".format(phjArgName,phjArgValue)
            
            if phjMustBeAbsentColumnList is not None:
                
                if isinstance(phjMustBeAbsentColumnList,list):
                    
                    # Check that all elements in phjArgValue list are absent from those
                    # contained in phjMustBeAbsentColumnList. This is done by converting
                    # lists to sets and finding the intersection (i.e. set(a) & set(b));
                    # the length of the resulting intersection should be zero.
                    assert len(list(set(phjArgValue) & set(phjMustBeAbsentColumnList))) == 0, "The elements in '{0}' ('{1}') already exist in list of columns'.".format(phjArgName,phjArgValue)
    
    except AssertionError as e:
        
        raise
    
    return


if __name__ == '__main__':
    main()

