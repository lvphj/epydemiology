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
    
    # Construct a generic message suffix to use for default message
    phjMessageSuffix = phjConstructGenericMessageSuffix(phjType)
    
    # Test that variable meets requirements and raise AssertionError if not
    # ---------------------------------------------------------------------
    try:
        # Test that variable is of the correct type
        # -----------------------------------------
        # If variable is a string, float, integer or boolean variable, check that
        # variable type is correct (as defined in phjType argument)
        if isinstance(phjVarValue,(str,float,int,bool)):
            assert isinstance(phjVarValue,phjType),"Argument '{0}' ('{1}') needs to be a {2}.".format(phjVarName,
                                                                                                      phjVarValue,
                                                                                                      phjMessageSuffix)
        
        # If variable is anything else (e.g. dataframe, list, dict, etc.) then check
        # variable type is correct (but message cannot refer to single value)
        else:
            assert isinstance(phjVarValue,phjType),"Argument '{0}' needs to be a {1}.".format(phjVarName,
                                                                                              phjMessageSuffix)
        
        
        # Test that variable is a correct value
        # -------------------------------------
        # Depending on the type of phjVarValue, check that value(s) are valid.
        #
        # If phjMustBePresentColumnList is not None then check that phjVarValue is valid
        if phjMustBePresentColumnList is not None:
            # If phjMustBePresentColumnList is a list, then check that phjVarValue is
            # included
            if isinstance(phjMustBePresentColumnList,list):
                # If phjVarValue is a string then check that it is listed
                if isinstance(phjVarValue,str):
                    if phjBespokeMessage is None:
                        assert phjVarValue in phjMustBePresentColumnList,"Variable '{0}' ('{1}') is not present in list of columns.".format(phjVarName,phjVarValue)
                    else:
                        assert phjVarValue in phjMustBePresentColumnList,phjBespokeMessage
                
                # If phjVarValue is a list then check that all items in phjVarValue list
                # are contained in the phjMustBePresentColumnList.
                elif isinstance(phjVarValue,list):
                    if phjBespokeMessage is None:
                        assert set(phjVarValue).issubset(phjMustBePresentColumnList), "The elements in '{0}' ('{1}') do not all exist in list of columns.".format(phjVarName,phjVarValue)
                    else:
                        assert set(phjVarValue).issubset(phjMustBePresentColumnList),phjBespokeMessage
            
            # phjMustBePresentColumnList may be a single string (even though it is not
            # not supposed to be)
            elif isinstance(phjMustBePresentColumnList,str):
                if phjBespokeMessage is None:
                    assert phjVarValue == phjMustBePresentColumnList,"Variable '{0}' ('{1}') must be '{2}'.".format(phjVarName,phjVarValue,phjMustBePresentColumnList)
                else:
                    assert phjVarValue == phjMustBePresentColumnList,phjBespokeMessage
        
        
        # If phjMustBeAbsentColumnList is not None than check that phjVarVaoue is valid
        if phjMustBeAbsentColumnList is not None:
            # If phjMustBeAbsentColumnList is a list, then check that phjVarValue is NOT
            # included in the phjMustBeAbsentColumnList
            if isinstance(phjMustBeAbsentList,list):
                # If phjVarValue is a string then check that it is NOT listed
                if isinstance(phjVarValue,str):
                    if phjBespokeMessage is None:
                        assert phjVarValue not in phjMustBeAbsentColumnList,"Variable '{}' already exists in the list of columns.".format(phjVarValue)
                    else:
                        assert phjVarValue not in phjMustBeAbsentColumnList,phjBespokeMessage
                
                # If phjVarValue is a list then check that ALL items in phjVarValue list
                # are absent from those contained in the phjMustBeAbsentColumnList.
                # This is done by converting lists to sets and finding the intersection
                # (i.e. set(a) & set(b)); the length of the resulting intersection should
                # be zero.
                elif isinstance(phjVarValue,list):
                    if phjBespokeMessage is None:
                        assert len(list(set(phjVarValue) & set(phjMustBeAbsentColumnList))) == 0, "The elements in '{0}' ('{1}') already exist in list of columns'.".format(phjVarName,phjVarValue)
                    else:
                        assert len(list(set(phjVarValue) & set(phjMustBeAbsentColumnList))) == 0,phjBespokeMessage
            
            # phjMustBeAbsentColumnList may be a single string
            elif isinstance(phjMustBeAbsentColumnList,str):
                if phjBespokeMessage is None:
                    assert phjVarValue == phjMustBeAbsentColumnList,"Variable '{}' must NOT be '{}'.".format(phjVarValue,phjMustBeAbsentColumnList1)
                else:
                    assert phjVarValue == phjMustBeAbsentColumnList,phjBespokeMessage
        
        
        # If phjAllowedOptions is set and phjVarValue is a string, int or float, then
        # check that variable value meets requirements.
        if (phjAllowedOptions is not None) & (isinstance(phjVarValue,(str,int,float))):
            # The phjAllowedOptions can be a list or a dictionary.
            # If phjAllowedOptions is a list then check that phjVarValue is in list
            # of allowed options
            if isinstance(phjAllowedOptions,list):
                if phjBespokeMessage is None:
                    assert phjVarValue in phjAllowedOptions, "Parameter '{0}' ('{1}') is not an allowed value.".format(phjVarName,phjVarValue)
                else:
                    assert phjVarValue in phjAllowedOptions,phjBespokeMessage
            
            
            # If the phjAllowedOptions argument is a dictionary that contains min
            # and max value which defines a range.
            elif isinstance(phjAllowedOptions,collections.Mapping): # collections.Mapping will work for dict(), collections.OrderedDict() and collections.UserDict() (see comment by Alexander Ryzhov at https://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python.
                if [k for k,v in phjAllowedOptions.items()] == ['min','max']:
                    if phjBespokeMessage is None:
                        assert (phjVarValue >= phjAllowedOptions['min']) & (phjVarValue <= phjAllowedOptions['max']), "Parameter '{0}' ('{1}') is outside the allowed range ({2} to {3}).".format(phjVarName,
                                                                                                                                                                                              phjVarValue,
                                                                                                                                                                                              phjAllowedOptions['min'],
                                                                                                                                                                                              phjAllowedOptions['max'])
                    else:
                        assert (phjVarValue >= phjAllowedOptions['min']) & (phjVarValue <= phjAllowedOptions['max']),phjBespokeMessage
    
    except AssertionError as e:
        
        raise
    
    return



def phjConstructGenericMessageSuffix(phjType):
    # Construct generic message suffix
    # --------------------------------
    # Construct generic message regarding permissable types. For example, if phjType
    # is a single value (e.g. str) then the message in the event of assert being False
    # would need to indicate that the type should be a 'string'. If phjType is a tuple
    # of potential values (e.g. (str,int,float,list)) then the message in the event of
    # assert being False would need to indicate that the required types should be
    # 'string, integer, float or list'.
    # phjMessageSuffix is a string that lists all viable options for variable type
    # (e.g. "str, int, float or list").
    
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
    
    return phjMessageSuffix



if __name__ == '__main__':
    main()

