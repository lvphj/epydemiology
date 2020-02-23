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



# This is an attempt to standardise the returns from assert() function.
# phjVarName is a string giving the name of variable.
# phjVarValue is the variable.
# phjType is the type that the variable must take. Can pass a tuple of types for multiple options.
# phjBespokeMessage is a message displayed in the event of an AssertionException instead of the generic message.
# phjMustBePresentColumnList is a string or a list of column names of which phjVarValue must be one.
# phjMustBeAbsentColumnList is a string or a list of column names in which phjVarValue must not be included.
# phjAllowedOptions can be a list or a dict containing 'min' and 'max' keys.
def phjAssert(phjVarName,
              phjVarValue,
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
        if isinstance(phjVarValue,(str,float,int,bool)):
            
            if phjBespokeMessage is None:
                assert isinstance(phjVarValue,phjType),"Argument '{0}' ('{1}') needs to be a {2}.".format(phjVarName,
                                                                                                          phjVarValue,
                                                                                                          phjMessageSuffix)
            
            else:
                assert isinstance(phjVarValue,phjType),phjBespokeMessage
                
        else:
            
            if phjBespokeMessage is None:
                assert isinstance(phjVarValue,phjType),"Argument '{0}' needs to be a {1}.".format(phjVarName,
                                                                                                  phjMessageSuffix)
            
            else:
                assert isinstance(phjVarValue,phjType),phjBespokeMessage
        
        
        # Depending on the type of passed variable phjVarValue, check that value lies
        # within correct limits.
        if isinstance(phjVarValue,str):
            
            # If phjMustBePresentColumnList parameter is set then check that phjVarValue is
            # indeed present in that list (e.g. list of dataframe column names).
            if phjMustBePresentColumnList is not None:
                
                # If phjMustBePresentColumnList is a list, then check that phjVarValue is included
                if isinstance(phjMustBePresentColumnList,list):
                    assert phjVarValue in phjMustBePresentColumnList,"Variable '{0}' ('{1}') is not present in list of columns.".format(phjVarName,phjVarValue)
                
                # phjMustBePresentColumnList may be a single string
                elif isinstance(phjMustBePresentColumnList,str):
                    assert phjVarValue == phjMustBePresentColumnList,"Variable '{0}' ('{1}') must be '{2}'.".format(phjVarName,phjVarValue,phjMustBePresentColumnList)
            
            # If phjMustBeAbsentColumnList parameter is set then check that phjVarValue is
            # not present in that list (e.g. list of dataframe column names).
            if phjMustBeAbsentColumnList is not None:
                
                # If phjMustBeAbsentColumnList is a list, then check that phjVarValue is NOT included
                if isinstance(phjMustBeAbsentColumnList,list):
                    assert phjVarValue not in phjMustBeAbsentColumnList,"Variable '{}' already exists in the list of columns.".format(phjVarValue)
                
                # phjMustBeAbsentColumnList may be a single string
                elif isinstance(phjMustBeAbsentColumnList,str):
                    assert phjVarValue == phjMustBeAbsentColumnList,"Variable '{}' must NOT be '{}'.".format(phjVarValue,phjMustBeAbsentColumnList1)
            
            if phjAllowedOptions is not None:
                # Cannot think of any reasons why allowed options would be a single value.
                # Therefore, the phjVarValue must be one of values included in list.
                if isinstance(phjAllowedOptions,list):
                    # If is a string then assert if string contained in list:
                    assert phjVarValue in phjAllowedOptions, "Parameter '{0}' ('{1}') is not an allowed value.".format(phjVarName,phjVarValue)
                
                
        # If phjVarValue is an int or a float then check that it is an allowed value in
        # the phjAllowedOptions list or is in range as set by the min and max values in
        # phjAllowedOptions dict.
        elif isinstance(phjVarValue,(int,float)):
            
            if phjAllowedOptions is not None:
                # Cannot think of any reasons why allowed options would be a single value.
                # Therefore, the phjVarValue must be one of values included in list or a
                # value that lies in a range.
                if isinstance(phjAllowedOptions,list):
                    assert phjVarValue in phjAllowedOptions, "Parameter '{0}' ('{1}') is not an allowed value.".format(phjVarName,phjVarValue)
            
                elif isinstance(phjAllowedOptions,collections.Mapping): # collections.Mapping will work for dict(), collections.OrderedDict() and collections.UserDict() (see comment by Alexander Ryzhov at https://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python.
                    assert (phjVarValue >= phjAllowedOptions['min']) & (phjVarValue <= phjAllowedOptions['max']), "Parameter '{0}' ('{1}') is outside the allowed range ({2} to {3}).".format(phjVarName,
                                                                                                                                                                                              phjVarValue,
                                                                                                                                                                                              phjAllowedOptions['min'],
                                                                                                                                                                                              phjAllowedOptions['max'])
        # If the phjVarValue is a list then check that all the items are all included
        # in the list of allowed options.
        elif isinstance(phjVarValue,list):
        
            if phjMustBePresentColumnList is not None:
            
                if isinstance(phjMustBePresentColumnList,list):
                    
                    # Check that all items in phjVarValue list are contained in the
                    # phjMustBePresentColumnList.
                    assert set(phjVarValue).issubset(phjMustBePresentColumnList), "The elements in '{0}' ('{1}') do not all exist in list of columns.".format(phjVarName,phjVarValue)
            
            if phjMustBeAbsentColumnList is not None:
                
                if isinstance(phjMustBeAbsentColumnList,list):
                    
                    # Check that all elements in phjVarValue list are absent from those
                    # contained in phjMustBeAbsentColumnList. This is done by converting
                    # lists to sets and finding the intersection (i.e. set(a) & set(b));
                    # the length of the resulting intersection should be zero.
                    assert len(list(set(phjVarValue) & set(phjMustBeAbsentColumnList))) == 0, "The elements in '{0}' ('{1}') already exist in list of columns'.".format(phjVarName,phjVarValue)
    
    except AssertionError as e:
        
        raise
    
    return


if __name__ == '__main__':
    main()

