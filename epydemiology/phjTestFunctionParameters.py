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
# phjArgValue is the function argument.
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
    
    # Construct a generic message suffix to use for default message
    phjMessageSuffix = phjConstructGenericMessageSuffix(phjType)
    
    # Test that variable meets requirements and raise AssertionError if not
    # ---------------------------------------------------------------------
    try:
        # Test that variable is of the correct type
        # -----------------------------------------
        # If variable is a string, float, integer or boolean variable, check that
        # variable type is correct (as defined in phjType argument)
        if isinstance(phjArgValue,(str,float,int,bool)):
            assert isinstance(phjArgValue,phjType),"Argument '{0}' ('{1}') needs to be a {2}.".format(phjArgName,
                                                                                                      phjArgValue,
                                                                                                      phjMessageSuffix)
        
        # If variable is anything else (e.g. dataframe, list, dict, etc.) then check
        # variable type is correct (but message cannot refer to single value)
        else:
            assert isinstance(phjArgValue,phjType),"Argument '{0}' needs to be a {1}.".format(phjArgName,
                                                                                              phjMessageSuffix)
        
        
        # Test that variable is a correct value
        # -------------------------------------
        # Depending on the type of phjArgValue, check that value(s) are valid.
        #
        # If phjMustBePresentColumnList is not None then check that phjArgValue is valid
        if phjMustBePresentColumnList is not None:
            # If phjMustBePresentColumnList is a list, then check that phjArgValue is
            # included
            if isinstance(phjMustBePresentColumnList,list):
                # If phjArgValue is a string then check that it is listed
                if isinstance(phjArgValue,str):
                    if phjBespokeMessage is None:
                        assert phjArgValue in phjMustBePresentColumnList,"Variable '{0}' ('{1}') is not present in list of columns.".format(phjArgName,phjArgValue)
                    else:
                        assert phjArgValue in phjMustBePresentColumnList,phjBespokeMessage
                
                # If phjArgValue is a list then check that all items in phjArgValue list
                # are contained in the phjMustBePresentColumnList.
                elif isinstance(phjArgValue,list):
                    if phjBespokeMessage is None:
                        assert set(phjArgValue).issubset(phjMustBePresentColumnList), "The elements in '{0}' ('{1}') do not all exist in list of columns.".format(phjArgName,phjArgValue)
                    else:
                        assert set(phjArgValue).issubset(phjMustBePresentColumnList),phjBespokeMessage
            
            # phjMustBePresentColumnList may be a single string (even though it is not
            # not supposed to be)
            elif isinstance(phjMustBePresentColumnList,str):
                if phjBespokeMessage is None:
                    assert phjArgValue == phjMustBePresentColumnList,"Variable '{0}' ('{1}') must be '{2}'.".format(phjArgName,phjArgValue,phjMustBePresentColumnList)
                else:
                    assert phjArgValue == phjMustBePresentColumnList,phjBespokeMessage
        
        
        # If phjMustBeAbsentColumnList is not None than check that phjVarVaoue is valid
        if phjMustBeAbsentColumnList is not None:
            # If phjMustBeAbsentColumnList is a list, then check that phjArgValue is NOT
            # included in the phjMustBeAbsentColumnList
            if isinstance(phjMustBeAbsentList,list):
                # If phjArgValue is a string then check that it is NOT listed
                if isinstance(phjArgValue,str):
                    if phjBespokeMessage is None:
                        assert phjArgValue not in phjMustBeAbsentColumnList,"Variable '{}' already exists in the list of columns.".format(phjArgValue)
                    else:
                        assert phjArgValue not in phjMustBeAbsentColumnList,phjBespokeMessage
                
                # If phjArgValue is a list then check that ALL items in phjArgValue list
                # are absent from those contained in the phjMustBeAbsentColumnList.
                # This is done by converting lists to sets and finding the intersection
                # (i.e. set(a) & set(b)); the length of the resulting intersection should
                # be zero.
                elif isinstance(phjArgValue,list):
                    if phjBespokeMessage is None:
                        assert len(list(set(phjArgValue) & set(phjMustBeAbsentColumnList))) == 0, "The elements in '{0}' ('{1}') already exist in list of columns'.".format(phjArgName,phjArgValue)
                    else:
                        assert len(list(set(phjArgValue) & set(phjMustBeAbsentColumnList))) == 0,phjBespokeMessage
            
            # phjMustBeAbsentColumnList may be a single string
            elif isinstance(phjMustBeAbsentColumnList,str):
                if phjBespokeMessage is None:
                    assert phjArgValue == phjMustBeAbsentColumnList,"Variable '{}' must NOT be '{}'.".format(phjArgValue,phjMustBeAbsentColumnList1)
                else:
                    assert phjArgValue == phjMustBeAbsentColumnList,phjBespokeMessage
        
        
        # If phjAllowedOptions is set and phjArgValue is a string, int or float, then
        # check that variable value meets requirements.
        if (phjAllowedOptions is not None) & (isinstance(phjArgValue,(str,int,float))):
            # The phjAllowedOptions can be a list or a dictionary.
            # If phjAllowedOptions is a list then check that phjArgValue is in list
            # of allowed options.
            # Potentially, could use collections.abc.Sequence instead of list to allow any
            # sequence type to be included
            # (see: https://stackoverflow.com/questions/35690572/what-does-isinstance-with-a-dictionary-and-abc-mapping-from-collections-doing).
            if isinstance(phjAllowedOptions,list):
                if phjBespokeMessage is None:
                    assert phjArgValue in phjAllowedOptions,"Parameter '{0}' ('{1}') is not an allowed value.".format(phjArgName,phjArgValue)
                else:
                    assert phjArgValue in phjAllowedOptions,phjBespokeMessage
            
            
            # If the phjAllowedOptions argument is a dictionary that contains min
            # and max value which defines a range.
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
                    if phjBespokeMessage is None:
                        assert (phjArgValue >= phjAllowedOptions['min']) & (phjArgValue <= phjAllowedOptions['max']), "Parameter '{0}' ('{1}') is outside the allowed range ({2} to {3}).".format(phjArgName,
                                                                                                                                                                                                  phjArgValue,
                                                                                                                                                                                                  phjAllowedOptions['min'],
                                                                                                                                                                                                  phjAllowedOptions['max'])
                    else:
                        assert (phjArgValue >= phjAllowedOptions['min']) & (phjArgValue <= phjAllowedOptions['max']),phjBespokeMessage
                    
                    
                elif collections.Counter([k for k,v in phjAllowedOptions.items()]) == collections.Counter(['min']):
                    if phjBespokeMessage is None:
                        assert (phjArgValue >= phjAllowedOptions['min']), "Parameter '{0}' ('{1}') is less than the allowed minimum value ({2}).".format(phjArgName,
                                                                                                                                                     phjArgValue,
                                                                                                                                                     phjAllowedOptions['min'])
                    else:
                        assert (phjArgValue >= phjAllowedOptions['min']),phjBespokeMessage
                    
                elif collections.Counter([k for k,v in phjAllowedOptions.items()]) == collections.Counter(['max']):
                    if phjBespokeMessage is None:
                        assert (phjArgValue <= phjAllowedOptions['max']), "Parameter '{0}' ('{1}') is greater than the allowed maximum value ({2}).".format(phjArgName,
                                                                                                                                                        phjArgValue,
                                                                                                                                                        phjAllowedOptions['max'])
                    else:
                        assert (phjArgValue <= phjAllowedOptions['max']),phjBespokeMessage
    
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
