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


def phjRemoveUnwantedRows(phjDF,
                          phjColumnNamesList,
                          phjPrintResults = False):
    
    # Remove any rows with one or more NaN values
    phjNumberRowsPreNaN = len(phjDF.index)
    
    phjDF = phjDF.dropna(how = 'any').reset_index(drop = True)
    
    phjNumberRowsPostNaN = len(phjDF.index)
    
    if phjPrintResults == True:
        print('Number of rows removed with NaN values = ', phjNumberRowsPreNaN - phjNumberRowsPostNaN)
        print('\n')
        print('Dataframe with NaN values removed')
        print(phjDF)
        print('\n')
    
    
    # Convert each column to numeric values - strings will be converted to NaN and removed
    phjNumberRowsPreStrings = len(phjDF.index)
    
    for c in phjColumnNamesList:
        phjDF[c] = pd.to_numeric(phjDF[c],errors = 'coerce')
    
    phjDF = phjDF.dropna(how = 'any').reset_index(drop = True)
        
    phjNumberRowsPostStrings = len(phjDF.index)
    
    if phjPrintResults == True:
        print('Number of rows removed due to containing string values = ', phjNumberRowsPreStrings - phjNumberRowsPostStrings)
        print('\n')
        print('Dataframe with strings values removed')
        print(phjDF)
        print('\n')


    # Convert all columns to integers
    for c in phjColumnNamesList:
        phjDF[c] = phjDF[c].astype(int)
    
    
    # Remove rows that contain values that are not zero or 1
    phjNumberRowsPreBinaryRange = len(phjDF.index)
    
    for c in phjColumnNamesList:
        phjDF['isin'] = phjDF[c].isin([0,1])
        phjDF = phjDF.loc[phjDF['isin'] == True,:]
    
    phjDF = phjDF.drop('isin', 1).reset_index(drop = True)
    
    phjNumberRowsPostBinaryRange = len(phjDF.index)

    if phjPrintResults == True:
        print('Number of rows removed due to values being out of range = ', phjNumberRowsPreBinaryRange - phjNumberRowsPostBinaryRange)
        print('\n')
        print('Dataframe containing zero and 1 values only')
        print(phjDF)
        print('\n')
    
    
    return phjDF[phjColumnNamesList].reset_index(drop = True)



def phjBinaryVarsToSquareMatrix(phjDataDF,
                                phjColumnNamesList,
                                phjOutputFormat = 'arr',
                                phjPrintResults = False):
    
    try:
        phjDF = phjDataDF[phjColumnNamesList]
        
    except KeyError as e:
        print('A KeyError has occurred ({0}). Check that the column names provided exist in the dataframe.'.format(e))
        return None
    
    phjNumberRowsOriginal = len(phjDF.index)
    
    if phjPrintResults == True:
        print('Number of rows in original database = ', phjNumberRowsOriginal)
        print('\n')
        print('Original dataframe')
        print(phjDF)
        print('\n')
    
    # Remove rows where any values are missing, strings, or not a zero or 1
    phjDF = phjRemoveUnwantedRows(phjDF = phjDF,
                                      phjColumnNamesList = phjColumnNamesList,
                                      phjPrintResults = phjPrintResults)
    
    
    phjDF['rowSum'] = phjDF[phjColumnNamesList].sum(axis=1)
    
    # Create a blank square matrix (in dataframe form) with column and row indices the same
    phjTempMatrixDF = pd.DataFrame(columns=phjColumnNamesList,index=phjColumnNamesList)
    
    # Start by completing the diagonal
    # ================================
    # Use just those rows with only a single entry (i.e. only one variable is entered).
    # Create a series containing the name of the variable and the sum of entries.
    # (For some reason, if the dataframe contains one or more rows where rowSum equals 1 then
    # the series contains integers but, if there are no rowSum values equal to 1 (and, therefore, the values
    # sum of the columns equal zero), then the series contains floats. Use astype(int) to avoid issues.)
    phjTempSer = phjDF.loc[phjDF['rowSum']==1,phjColumnNamesList].sum(axis=0).astype(int)
    
    # Step through each diagonal cell in the matrix and enter tbe sum value
    for c in phjColumnNamesList:
        phjTempMatrixDF.loc[c,c]=phjTempSer[c]
    
    # Next fill in the rest of the matrix
    # ===================================
    # Step through each variable in the list and create a series consisting
    # of all OTHER variables and the number of entries or those variables
    for c in phjColumnNamesList:
        phjOtherCols = [i for i in phjColumnNamesList if i!=c]
        phjTempSer = phjDF.loc[(phjDF['rowSum']>1) & (phjDF[c]==1),phjOtherCols].sum(axis=0).astype(int)
        
        # For each row index, step through each column and add the data
        for oc in phjOtherCols:
            phjTempMatrixDF.loc[c,oc] = phjTempSer[oc]
    
    if phjPrintResults == True:
        print('Square matrix')
        print(phjTempMatrixDF)
        print('\n')
        
    if phjOutputFormat == 'arr':
        return phjTempMatrixDF.values
        
    elif phjOutputFormat == 'df':
        return phjTempMatrixDF
        
    else:
        print('The phjOutputFormat parammeter was set to an unknown value (\'{0}\'). The return value was set to None.'.format(phjOutputFormat))
        print('\n')
        return None



def phjLongToWideBinary(phjDF,
                        phjGroupbyVarName,
                        phjVariablesVarName,
                        phjValuesDict = {0:0,1:1},
                        phjPrintResults = False):
    # This function converts a dataframe containing a grouping variable and a variable
    # containing a series of factors that may or may not be present and converts to a
    # wide dataframe containing a series of binary variables indicating whether the factor
    # is present or not.
    # For example, it converts:
    #
    #       X  Y
    #    0  1  a
    #    1  1  b
    #    2  1  d
    #    3  2  b
    #    4  2  c
    #    5  3  d
    #    6  3  e
    #    7  3  a
    #    8  3  f
    #    9  4  b
    # 
    # to:
    #       X  a  b  d  c  e  f
    #    0  1  1  1  1  0  0  0
    #    1  2  0  1  0  1  0  0
    #    2  3  1  0  1  0  1  1
    #    3  4  0  1  0  0  0  0
    
    
    # Check function parameters are set correctly
    try:
        # Check whether required parameters have been set to correct type
        assert isinstance(phjDF,pd.DataFrame), "Parameter, 'phjDF' needs to be a Pandas dataframe."
        assert isinstance(phjGroupbyVarName,str), "Parameter 'phjGroupbyVarName' needs to be a string."
        assert isinstance(phjVariablesVarName,str), "Parameter 'phjVariablesVarName' needs to be a string."
        assert isinstance(phjValuesDict,collections.Mapping), "Parameter 'phjValuesDict' needs to be a dict." # collections.Mapping will work for dict(), collections.OrderedDict() and collections.UserDict() (see comment by Alexander Ryzhov at https://stackoverflow.com/questions/25231989/how-to-check-if-a-variable-is-a-dictionary-in-python.
                
        # Check whether arguments are set to allowable values
        for k,v in phjValuesDict.items():
            assert k in [0,1], "The key values in phjValuesDict need to either 0 or 1."
            
        assert isinstance(phjPrintResults,bool), "Parameter 'phjPrintResults' needs to be a boolean (True, False) value."
        
        # Check that referenced columns exist in the dataframe
        assert phjGroupbyVarName in phjDF.columns, "The column name 'phjGroupbyVarName' does not exist in dataframe."
        assert phjVariablesVarName in phjDF.columns, "The column name 'phjVariablesVarName' does not exist in dataframe."
        
    except AssertionError as e:
        # Set return value to none
        phjScratchDF = None
        
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
            raise
        
    else:
        # Create a scratch DF with appropriate rows and columns, filled with zero
        phjScratchDF = pd.DataFrame(index = pd.Series(phjDF[phjGroupbyVarName].unique()),
                                    columns = list(phjDF[phjVariablesVarName].unique())).fillna(0)

        phjScratchDF.index.name = phjGroupbyVarName

        # Within each group, create a list contain all variables
        phjGroup = phjDF[[phjGroupbyVarName,phjVariablesVarName]].groupby(phjGroupbyVarName).agg(lambda phjRow: list(phjRow))

        # Step through each group and change each variable contained in the list of present variables with a 1
        for g in phjGroup.index.values.tolist():
            phjScratchDF.loc[g,phjGroup.loc[g,phjVariablesVarName]] = 1
        
        # This step replaces the default 0 and 1 with user-defined values. It should only be
        # run if phjValuesDict has been set to something other than default. Check whether
        # a passed dict is the same as the default (even if the order of elements has changed).
        # If simply comparing one dict with another then {0:0,1:1} will be seen to be the
        # same as {0:False,1:True}. But for the purposes of this exercise, those 2 dicts should
        # be seen to be different. Therefore, convert the values is both dicts to strings
        # before comparing.
        if {k:str(v) for k,v in phjValuesDict.items()} != {k:str(v) for k,v in {0:0,1:1}.items()}:
            phjScratchDF = phjScratchDF.replace(phjValuesDict)
        
        phjScratchDF = phjScratchDF.reset_index(drop = False)
    
    finally:
        # Return phjScratchDF which will be a dataframe if successful or None if not
        return phjScratchDF



if __name__ == '__main__':
    main()
