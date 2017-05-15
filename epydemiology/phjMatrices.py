import numpy as np
import pandas as pd

def phjRemoveUnwantedRows(phjTempDF,
                          phjColumnNamesList,
                          phjPrintResults):
    
    # Remove any rows with one or more NaN values
    phjNumberRowsPreNaN = len(phjTempDF.index)
    
    phjTempDF = phjTempDF.dropna(how = 'any').reset_index(drop = True)
    
    phjNumberRowsPostNaN = len(phjTempDF.index)
    
    if phjPrintResults == True:
        print('Number of rows removed with NaN values = ', phjNumberRowsPreNaN - phjNumberRowsPostNaN)
        print('\n')
        print('Dataframe with NaN values removed')
        print(phjTempDF)
        print('\n')
    
    
    # Convert each column to numeric values - strings will be converted to NaN and removed
    phjNumberRowsPreStrings = len(phjTempDF.index)
    
    for c in phjColumnNamesList:
        phjTempDF[c] = pd.to_numeric(phjTempDF[c],errors = 'coerce')
    
    phjTempDF = phjTempDF.dropna(how = 'any').reset_index(drop = True)
        
    phjNumberRowsPostStrings = len(phjTempDF.index)
    
    if phjPrintResults == True:
        print('Number of rows removed due to containing string values = ', phjNumberRowsPreStrings - phjNumberRowsPostStrings)
        print('\n')
        print('Dataframe with strings values removed')
        print(phjTempDF)
        print('\n')


    # Convert all columns to integers
    for c in phjColumnNamesList:
        phjTempDF[c] = phjTempDF[c].astype(int)
    
    
    # Remove rows that contain values that are not zero or 1
    phjNumberRowsPreBinaryRange = len(phjTempDF.index)
    
    for c in phjColumnNamesList:
        phjTempDF['isin'] = phjTempDF[c].isin([0,1])
        phjTempDF = phjTempDF.loc[phjTempDF['isin'] == True,:]
    
    phjTempDF = phjTempDF.drop('isin', 1).reset_index(drop = True)
    
    phjNumberRowsPostBinaryRange = len(phjTempDF.index)

    if phjPrintResults == True:
        print('Number of rows removed due to values being out of range = ', phjNumberRowsPreBinaryRange - phjNumberRowsPostBinaryRange)
        print('\n')
        print('Dataframe containing zero and 1 values only')
        print(phjTempDF)
        print('\n')
    
    
    return phjTempDF[phjColumnNamesList].reset_index(drop = True)



def phjBinaryVarsToSquareMatrix(phjDataDF,
                                phjColumnNamesList,
                                phjOutputFormat = 'arr',
                                phjPrintResults = False):
    
    try:
        phjTempDF = phjDataDF[phjColumnNamesList]
        
    except KeyError as e:
        print('A KeyError has occurred ({0}). Check that the column names provided exist in the dataframe.'.format(e))
        return None
    
    phjNumberRowsOriginal = len(phjTempDF.index)
    
    if phjPrintResults == True:
        print('Number of rows in original database = ', phjNumberRowsOriginal)
        print('\n')
        print('Original dataframe')
        print(phjTempDF)
        print('\n')
    
    # Remove rows where any values are missing, strings, or not a zero or 1
    phjTempDF = phjRemoveUnwantedRows(phjTempDF = phjTempDF,
                                      phjColumnNamesList = phjColumnNamesList,
                                      phjPrintResults = phjPrintResults)
    
    
    phjTempDF['rowSum'] = phjTempDF[phjColumnNamesList].sum(axis=1)
    
    # Create a blank square matrix (in dataframe form) with column and row indices the same
    phjTempMatrixDF = pd.DataFrame(columns=phjColumnNamesList,index=phjColumnNamesList)
    
    # Start by completing the diagonal
    # ================================
    # Use just those rows with only a single entry (i.e. only one variable is entered).
    # Create a series containing the name of the variable and the sum of entries.
    # (For some reason, if the dataframe contains one or more rows where rowSum equals 1 then
    # the series contains integers but, if there are no rowSum values equal to 1 (and, therefore, the values
    # sum of the columns equal zero), then the series contains floats. Use astype(int) to avoid issues.)
    phjTempSer = phjTempDF.loc[phjTempDF['rowSum']==1,phjColumnNamesList].sum(axis=0).astype(int)
    
    # Step through each diagonal cell in the matrix and enter tbe sum value
    for c in phjColumnNamesList:
        phjTempMatrixDF.loc[c,c]=phjTempSer[c]
    
    # Next fill in the rest of the matrix
    # ===================================
    # Step through each variable in the list and create a series consisting
    # of all OTHER variables and the number of entries or those variables
    for c in phjColumnNamesList:
        phjOtherCols = [i for i in phjColumnNamesList if i!=c]
        phjTempSer = phjTempDF.loc[(phjTempDF['rowSum']>1) & (phjTempDF[c]==1),phjOtherCols].sum(axis=0).astype(int)
        
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
