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


try:
    pkg_resources.get_distribution('scipy')
except pkg_resources.DistributionNotFound:
    scipyPresent = False
    print("Error: Scipy package not available.")
else:
    scipyPresent = True
    from scipy.stats import norm


import math


# Import minor epydemiology functions from other epydemiology files
# -----------------------------------------------------------------
# In order to use the phjDefineSuffixDict() function from a different .py file in the
# same package, it seems that we need to import that function explicitly. This can be
# done using the same format as in the __init__.py file e.g.:
#     from .pythonFileName import functionName
# Where the pythonFileName is a file in the same package.
# For more details, see tutorial at https://www.youtube.com/watch?v=0oTh1CXRaQ0.

from .phjCalculateProportions import phjDefineSuffixDict



def phjOddsRatio(phjDF,
                 phjCaseVarName,
                 phjCaseValue,
                 phjRiskFactorVarName,
                 phjRiskFactorBaseValue,
                 phjMissingValue = np.nan,
                 phjAlpha = 0.05,
                 phjPrintResults = False):
    
    # Call the phjRatios() function to do the work
    phjContTable = phjRatios(phjDF = phjDF,
                             phjRatioType = 'oddsratio',    # Should be one of the keys in phjSuffixDict
                             phjCaseVarName = phjCaseVarName,
                             phjCaseValue = phjCaseValue,
                             phjRiskFactorVarName = phjRiskFactorVarName,
                             phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                             phjMissingValue = phjMissingValue,
                             phjAlpha = phjAlpha,
                             phjPrintResults = phjPrintResults)
    
    return phjContTable




def phjRelativeRisk(phjDF,
                    phjCaseVarName,
                    phjCaseValue,
                    phjRiskFactorVarName,
                    phjRiskFactorBaseValue,
                    phjMissingValue = np.nan,
                    phjAlpha = 0.05,
                    phjPrintResults = False):
    
    # Call the phjRatios() function to do the work
    phjContTable = phjRatios(phjDF = phjDF,
                             phjRatioType = 'relrisk',    # Should be one of the keys in phjSuffixDict
                             phjCaseVarName = phjCaseVarName,
                             phjCaseValue = phjCaseValue,
                             phjRiskFactorVarName = phjRiskFactorVarName,
                             phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                             phjMissingValue = phjMissingValue,
                             phjAlpha = phjAlpha,
                             phjPrintResults = phjPrintResults)
    
    return phjContTable




def phjRatios(phjDF,
              phjRatioType,    # Should be one of the keys in phjSuffixDict
              phjCaseVarName,
              phjCaseValue,
              phjRiskFactorVarName,
              phjRiskFactorBaseValue,
              phjMissingValue = np.nan,
              phjAlpha = 0.05,
              phjPrintResults = False):
    
    # Set default suffixes and join strings to create column names
    # to use in output tables and dataframes.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Retain only those columns that will be analysed (otherwise, it is feasible that
    # unrelated columns that contain np.nan values will cause removal of rows in
    # unexpected ways.
    phjDF = phjDF[[phjCaseVarName,phjRiskFactorVarName]]
    
    # Check passed parameters are useable
    phjCheckPassed = phjRRORCheckArgs(phjDF = phjDF,
                                      phjCaseVarName = phjCaseVarName,
                                      phjCaseValue = phjCaseValue,
                                      phjRiskFactorVarName = phjRiskFactorVarName,
                                      phjRiskFactorBaseValue = phjRiskFactorBaseValue)
    
    if phjCheckPassed:
        # Data to use - remove rows that have a missing value
        phjDF = phjRemoveNaNRows(phjDF = phjDF,
                                     phjCaseVarName = phjCaseVarName,
                                     phjRiskFactorVarName = phjRiskFactorVarName,
                                     phjMissingValue = phjMissingValue)
        
        # Create a basic 2 x 2 (or n x 2) contingency table
        phjContTable = phjCreateContingencyTable(phjDF = phjDF,
                                                 phjCaseVarName = phjCaseVarName,
                                                 phjCaseValue = phjCaseValue,
                                                 phjRiskFactorVarName = phjRiskFactorVarName,
                                                 phjRiskFactorBaseValue = phjRiskFactorBaseValue)
        
        # Identify the code or string that represents a control value. (Take
        # all the column headings – there are only 2 of them – and convert
        # to list. Removing the case value will leave the control value.)
        phjControlValue = phjContTable.columns.tolist()
        phjControlValue.remove(phjCaseValue)
        phjControlValue = phjControlValue[0]
        # ... and add both values to a list in the right order
        # **** TO ENSURE COLUMNS ARE CORRECTLY REFERENCED, MAY BE NECESSARY TO CONVERT INT VALUES TO STR --- CHECK!!!
        phjCaseControlValuesList = [phjCaseValue,phjControlValue]
        
        if phjRatioType == 'relrisk':
            # If relative risk then add an extra column containing total number (i.e. cases plus controls)
            phjContTable[phjSuffixDict['totalnumber']] = phjContTable[phjCaseValue] + phjContTable[phjControlValue]
            
            # Calculate risks for each row
            phjContTable[phjSuffixDict['risk']] = phjContTable[phjCaseValue] / phjContTable[phjSuffixDict['totalnumber']]
            
            # Calculate risk ratios and confidence intervals.
            # Values are added to new columns in the phjContTable.
            phjContTable = phjCalcRRORwithCI(phjTempContDF = phjContTable,
                                             phjRatioType = phjRatioType,    # Should be one of the keys in phjSuffixDict
                                             phjCaseControlValuesList = phjCaseControlValuesList,
                                             phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                                             phjAlpha = 0.05,
                                             phjPrintResults = phjPrintResults)
        
        elif phjRatioType == 'oddsratio':
            # Calculate odds for each row
            phjContTable[phjSuffixDict['odds']] = phjContTable[phjCaseValue] / phjContTable[phjControlValue]
            
            # Calculate odds ratio and confidence intervals
            phjContTable = phjCalcRRORwithCI(phjTempContDF = phjContTable,
                                             phjRatioType = phjRatioType,    # Should be one of the keys in phjSuffixDict
                                             phjCaseControlValuesList = phjCaseControlValuesList,
                                             phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                                             phjAlpha = 0.05,
                                             phjPrintResults = phjPrintResults)
        
        else:
            phjContTable = None
        
        
        if phjPrintResults == True:
            if phjRatioType == 'relrisk':
                print("\nTable showing relative risk for risk factor strata with '{0}' considered as the base value.".format(phjRiskFactorBaseValue))
            elif phjRatioType == 'oddsratio':
                print("\nTable showing odds ratio for risk factor strata with '{0}' considered as the base value.".format(phjRiskFactorBaseValue))
            print(phjContTable)
            print('\n')
    
    
    else:
        print("\nArguments entered did not pass the test.")
        phjContTable = None
    
    return phjContTable




def phjRRORCheckArgs(phjDF,
                    phjCaseVarName,
                    phjCaseValue,
                    phjRiskFactorVarName,
                    phjRiskFactorBaseValue):
    
    # Check cases variable occurs and there are only 2 categories
    phjCheckPassed = phjCaseVarCheck(phjDF = phjDF,
                                     phjCaseVarName = phjCaseVarName)
    
    # Check values occur in variables.
    # BUT only need to do this if phjCheckPassed is True. If if is False then do not
    # change it back to True.
    if phjCheckPassed == True:
        for i,j in [[phjCaseValue,phjCaseVarName],[phjRiskFactorBaseValue,phjRiskFactorVarName]]:
            if phjCheckPassed == True:
                phjCheckPassed = phjValueCheck(phjDF = phjDF,
                                               phjVarName = j,
                                               phjValue = i)
    
    return phjCheckPassed



def phjCaseVarCheck(phjDF,
                    phjCaseVarName):
    
    # This function checks the following:
    # i.  The name passed to the function giving the case variable actually exists in the dataframe
    # ii. The case variable contains only 2 levels
    try:
        assert phjCaseVarName in phjDF.columns, 'The selected name for the case variable does not exist in the dataframe.'
        phjCheckPassed = True
        
        # Check that case variable contains 2 and only 2 levels
        try:
            assert phjDF[phjCaseVarName].nunique() == 2, 'The selected variable must contain only 2 levels, one representing a case and one a control.'
            phjCheckPassed = True
            
        except AssertionError as e:
            print(e)
            phjCheckPassed = False

    except AssertionError as e:
        print(e)
        phjCheckPassed = False
    
    return phjCheckPassed



def phjValueCheck(phjDF,
                  phjVarName,
                  phjValue):
    
    # This function check that values passed to the function actually exist in the variable where they are supposed to occur,
    # e.g. if a case is identified with 'y', make sure that 'y' occurs in the case variable.
    try:
        assert phjValue in phjDF[phjVarName].unique(),'The value {0} does not exist in variable {1}.'.format(phjValue,phjVarName)
        phjCheckPassed = True
        
    except AssertionError as e:
        print(e)
        phjCheckPassed = False
        
    return phjCheckPassed



def phjCaseFirst(phjDF,
                 phjCaseValue):
    
    # Creates a list with case value first. This can be used to order the dataframe columns
    phjCaseOrder = phjDF.columns.tolist()
    
    phjCaseOrder.remove(phjCaseValue)
    
    phjNewCaseOrder = [phjCaseValue] + phjCaseOrder
    
    # Return a list containing cases and controls with cases column coming first
    return phjNewCaseOrder



def phjRemoveNaNRows(phjDF,
                     phjCaseVarName,
                     phjRiskFactorVarName,
                     phjMissingValue = np.nan):
    
    # Replace empty cells with np.nan
    phjDF = phjDF.replace('',np.nan)
    
    # Replace missing values with np.nan
    if isinstance(phjMissingValue,str):
        phjDF = phjDF.replace(phjMissingValue,np.nan)
        
    elif not np.isnan(phjMissingValue):
        phjDF = phjDF.replace(phjMissingValue,np.nan)
    
    # Remove np.nan cells
    phjDF = phjDF[[phjCaseVarName,phjRiskFactorVarName]].dropna(axis = 0, how = 'any').reset_index(drop = True)
    
    return phjDF



def phjCreateContingencyTable(phjDF,
                              phjCaseVarName,
                              phjCaseValue,
                              phjRiskFactorVarName,
                              phjRiskFactorBaseValue):

    # Calculated univariable contingency table with risk factor levels as index and
    # cases and controls as columns.
    phjContTable = pd.crosstab(phjDF[phjRiskFactorVarName],phjDF[phjCaseVarName])
    
    # Rearrange the order of columns so that cases come first
    # N.B. There was a bug in Pandas 0.19.2 that resulted in re-ordered dataframe columns
    # being accessed in the wrong order. This did not affect the calculation of odds ratios
    # or 95% CI. The bug was reported to Pandas GitHub on 28 Mar 2017.
    phjContTable = phjContTable[phjCaseFirst(phjDF = phjContTable,
                                             phjCaseValue = phjCaseValue)]
    
    return phjContTable



def phjCalcRRORwithCI(phjTempContDF,
                      phjRatioType,
                      phjCaseControlValuesList = None,
                      phjRiskFactorBaseValue = None,
                      phjAlpha = 0.05,
                      phjPrintResults = False):
    
    # Set default suffixes and join strings to create column names
    # to use in output tables and dataframes.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Create lists of risk factor strata (including base strata) using the index
    phjRiskFactorStrataList = list(phjTempContDF.index)
    
    # The ratio method and the method used to calculate the CI should be named after
    # one of the keys in phjSuffixDict and then the column headings can be readily
    # defined in the dictionary
    if phjRatioType == 'relrisk':
        # Determine which form of risk ratio and confidence interval to calculate.
        # Default to opt for Katz log but, if any cells equal zero then opt for adjusted.
        if phjTempContDF[phjCaseControlValuesList].min(axis = 0).min(axis = 0) > 0:
            
            # The methods should reference keys in phjSuffixDict so column
            # headings can be readily labelled
            phjCIMethod = 'katz'
            
            # Create a list containing names for new column headings
            phjCIColsNamesList = phjCreateCIColsNamesList(phjRatioType = phjRatioType,
                                                          phjCIMethod = phjCIMethod,
                                                          phjAlpha = phjAlpha)
            
            # Add empty columns (with correct headings) to dataframe
            phjTempContDF = phjAddEmptyColumns(phjTempContDF = phjTempContDF,
                                               phjRiskFactorStrataList = phjRiskFactorStrataList,
                                               phjCIColsNamesList = phjCIColsNamesList)
            
            # Calculate relative risk or odds ratio and populate the table with values
            phjTempContDF = phjAddRatioAndCIValues(phjTempContDF = phjTempContDF,
                                                   phjCIMethod = phjCIMethod,
                                                   phjCaseControlValuesList = phjCaseControlValuesList,
                                                   phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                                                   phjCIColsNamesList = phjCIColsNamesList,
                                                   phjAlpha = phjAlpha)
        
        else:
            # One or more of the cells contains a zero value
            phjCIMethod = 'adj_log'
            
            # Create a list containing names for new column headings
            phjCIColsNamesList = phjCreateCIColsNamesList(phjRatioType = phjRatioType,
                                                          phjCIMethod = phjCIMethod,
                                                          phjAlpha = phjAlpha)
            
            # Add empty columns (with correct headings) to dataframe
            phjTempContDF = phjAddEmptyColumns(phjTempContDF = phjTempContDF,
                                               phjRiskFactorStrataList = phjRiskFactorStrataList,
                                               phjCIColsNamesList = phjCIColsNamesList)
            
            # Calculate relative risk or odds ratio and populate the table with values
            phjTempContDF = phjAddRatioAndCIValues(phjTempContDF = phjTempContDF,
                                                   phjCIMethod = phjCIMethod,
                                                   phjCaseControlValuesList = phjCaseControlValuesList,
                                                   phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                                                   phjCIColsNamesList = phjCIColsNamesList,
                                                   phjAlpha = phjAlpha)
    
    elif phjRatioType == 'oddsratio':
        # Determine which form of confidence interval to calculate and
        # create a list of column names for lower and upper CI limits, respectively.
        # If any of the cell values are zero, then calculation of Woolf's logit CIs will
        # fail due to division by zero. In small sample sizes, the Gart adjusted CI is
        # preferable. This is a modification of the Woolf CI which simply involves adding
        # 0.5 to each cell value.
        # What is a small sample size? No idea. But for the purposes of this exercise,
        # let's assume each cell contains at least 1 count. So, if any cell contains less
        # than 1 count, use the Gart-adjusted CI instead of Woolf.
        # Calculate the minimum value in each column and then the minimum value of
        # those minimum values.
        if phjTempContDF[phjCaseControlValuesList].min(axis = 0).min(axis = 0) > 0:
            
            phjCIMethod = 'woolf'
            
            # Create a list containing names for new column headings
            phjCIColsNamesList = phjCreateCIColsNamesList(phjRatioType = phjRatioType,
                                                          phjCIMethod = phjCIMethod,
                                                          phjAlpha = phjAlpha)
            
            # Add empty columns (with correct headings) to dataframe
            phjTempContDF = phjAddEmptyColumns(phjTempContDF = phjTempContDF,
                                               phjRiskFactorStrataList = phjRiskFactorStrataList,
                                               phjCIColsNamesList = phjCIColsNamesList)
            
            # Calculate relative risk or odds ratio and populate the table with values
            phjTempContDF = phjAddRatioAndCIValues(phjTempContDF = phjTempContDF,
                                                   phjCIMethod = phjCIMethod,
                                                   phjCaseControlValuesList = phjCaseControlValuesList,
                                                   phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                                                   phjCIColsNamesList = phjCIColsNamesList,
                                                   phjAlpha = phjAlpha)
        
        
        else:
            # For small sample sizes, the Woolf CI is adjusted and is called the Gart CI
            phjCIMethod = 'gart'
            
            # Create a list containing names for new column headings
            phjCIColsNamesList = phjCreateCIColsNamesList(phjRatioType = phjRatioType,
                                                          phjCIMethod = phjCIMethod,
                                                          phjAlpha = phjAlpha)
            
            # Add empty columns (with correct headings) to dataframe
            phjTempContDF = phjAddEmptyColumns(phjTempContDF = phjTempContDF,
                                               phjRiskFactorStrataList = phjRiskFactorStrataList,
                                               phjCIColsNamesList = phjCIColsNamesList)
            
            # Calculate relative risk or odds ratio and populate the table with values
            phjTempContDF = phjAddRatioAndCIValues(phjTempContDF = phjTempContDF,
                                                   phjCIMethod = phjCIMethod,
                                                   phjCaseControlValuesList = phjCaseControlValuesList,
                                                   phjRiskFactorBaseValue = phjRiskFactorBaseValue,
                                                   phjCIColsNamesList = phjCIColsNamesList,
                                                   phjAlpha = phjAlpha)
    
    else:
        print("Requested ratio method not implemented.")
        phjTempContDF = phjTempContDF
    
    
    return phjTempContDF



def phjCreateCIColsNamesList(phjRatioType,
                             phjCIMethod,
                             phjAlpha = 0.05):
    
    # Set default suffixes and join strings to create column names
    # to use in output tables and dataframes.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)

    # Create a list of column names for ratio, lower and upper CI limits, respectively.
    phjCIColsNamesList = [phjSuffixDict[phjRatioType],
                          phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],
                                                         phjSuffixDict[phjCIMethod],
                                                         phjSuffixDict['cilowlim']]),
                          phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],
                                                         phjSuffixDict[phjCIMethod],
                                                         phjSuffixDict['ciupplim']])]
    
    return phjCIColsNamesList



def phjAddEmptyColumns(phjTempContDF,
                       phjRiskFactorStrataList,
                       phjCIColsNamesList):
    
    # Create an empty dataframe containing '---' values and join it to the main dataframe.
    # Originally, it was intended to create a table containing CI only but, for some
    # approximations, it is necessary to access the original cell counts. Therefore, the
    # whole dataframe is passed to this function and empty columns added to it, later to
    # be filled with calculated values.
    phjEmptyDF = pd.DataFrame(index = phjRiskFactorStrataList,columns = phjCIColsNamesList).fillna('---')
    phjTempContDF = phjTempContDF.join(phjEmptyDF)
    
    return phjTempContDF



def phjAddRatioAndCIValues(phjTempContDF,
                           phjCIMethod,
                           phjCaseControlValuesList,
                           phjRiskFactorBaseValue,
                           phjCIColsNamesList,
                           phjAlpha = 0.05):
    
    # Set default suffixes and join strings to create column names
    # to use in output tables and dataframes.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Create lists of risk factor strata (including base strata) using the index
    phjRiskFactorStrataList = list(phjTempContDF.index)
    
    if phjCIMethod == 'katz':
        # Calculate relative risk
        phjTempContDF[phjSuffixDict['relrisk']] = phjTempContDF[phjSuffixDict['risk']] / phjTempContDF.loc[phjRiskFactorBaseValue,phjSuffixDict['risk']]
        
        # Calculate confidence intervals
        # Step through each stratum of the risk factor (except the base value)
        phjRiskFactorStrataList.remove(phjRiskFactorBaseValue)
        for phjStratum in phjRiskFactorStrataList:
            # Create a dictionary containing cells a, b, c and d
            phjCellValuesDict = phjDefineCellValuesDict(phjTempContDF = phjTempContDF,
                                                        phjStratum = phjStratum,
                                                        phjCaseControlValuesList = phjCaseControlValuesList,
                                                        phjRiskFactorBaseValue = phjRiskFactorBaseValue)
            
            # Calculate SE of natural log of relative risk.
            # SE of log of RR is calulcated as sqrt( b/(a(a+b)) + d/(c(c+d)) ).
            # Alternatively, sqrt( 1/a + 1/c - 1/(a+b) - 1/(c+d))
            phjLogSE = math.sqrt( ( phjCellValuesDict['b'] / ( phjCellValuesDict['a']*( phjCellValuesDict['a'] + phjCellValuesDict['b'] ) ) ) +
                               ( phjCellValuesDict['d'] / ( phjCellValuesDict['c']*( phjCellValuesDict['c'] + phjCellValuesDict['d'] ) ) ) )
            
            # Calculate 95% CI.
            # Returned as a list in order of lower limit and upper limit.
            phjRiskFactorCIList = phjCalcCI_lognormal(phjUntransformedPointEstimate = phjTempContDF.loc[phjStratum,phjSuffixDict['relrisk']],
                                                      phjTransformedSE = phjLogSE,
                                                      phjAlpha = phjAlpha)
            
            # Add 95CI values to dataframe
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[1]] = phjRiskFactorCIList[0]
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[2]] = phjRiskFactorCIList[1]
    
    
    elif phjCIMethod == 'adj_log':
        # Step through each stratum of the risk factor (except the base value)
        phjRiskFactorStrataList.remove(phjRiskFactorBaseValue)
        for phjStratum in phjRiskFactorStrataList:
            # Create a dictionary containing cells a, b, c and d
            phjCellValuesDict = phjDefineCellValuesDict(phjTempContDF = phjTempContDF,
                                                        phjStratum = phjStratum,
                                                        phjCaseControlValuesList = phjCaseControlValuesList,
                                                        phjRiskFactorBaseValue = phjRiskFactorBaseValue)
            
            # Estimate relative risk (since at least one of the cell values is zero)
            # (Ref: Morten et al (2011_. Recommended confidence intervals for two independent
            #       binomial proportions. Statistical Methods in Medical Research 0(0) 1–31; see page 14)
            phjTempContDF.loc[phjStratum,phjSuffixDict['relrisk']] = ((phjCellValuesDict['a'] + 0.5) / (phjCellValuesDict['a'] + phjCellValuesDict['b'] + 0.5)) / ((phjCellValuesDict['c'] + 0.5) / (phjCellValuesDict['c'] + phjCellValuesDict['d'] + 0.5))
            
            # Calculate SE of natural log of relative risk.
            # Adjusted SE of log of RR is calulcated as sqrt( 1/(a + 0.5) + 1/(c + 0.5) - 1/((a+b) + 0.5) - 1/((c+d) + 0.5) ).
            # Alternatively, sqrt( 1/a + 1/c - 1/(a+b) - 1/(c+d))
            phjLogSE = math.sqrt( (1 / (phjCellValuesDict['a'] + 0.5)) +
                               (1 / (phjCellValuesDict['c'] + 0.5)) -
                               (1 / (phjCellValuesDict['a'] + phjCellValuesDict['b'] + 0.5)) -
                               (1 / (phjCellValuesDict['c'] + phjCellValuesDict['d'] + 0.5)))
            
            # Calculate 95% CI
            phjRiskFactorCIList = phjCalcCI_lognormal(phjUntransformedPointEstimate = phjTempContDF.loc[phjStratum,phjSuffixDict['relrisk']],
                                                      phjTransformedSE = phjLogSE,
                                                      phjAlpha = phjAlpha)
            
            # Add list of 95CI to dataframe
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[1]] = phjRiskFactorCIList[0]
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[2]] = phjRiskFactorCIList[1]
    
    
    elif phjCIMethod == 'woolf':
        # Calculate odds ratio
        phjTempContDF[phjSuffixDict['oddsratio']] = phjTempContDF[phjSuffixDict['odds']] / phjTempContDF.loc[phjRiskFactorBaseValue,phjSuffixDict['odds']]
        
        # Calculate confidence intervals
        # Step through each stratum of the risk factor (except the base value)
        phjRiskFactorStrataList.remove(phjRiskFactorBaseValue)
        for phjStratum in phjRiskFactorStrataList:
            # Produce a list that contains the values contained in risk factor stratum and base stratum
            # The following is a list comprehension of the form given below. It was given by Alex Martelli at:
            # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
            # myList = [item for sublist in tempList for item in sublist].
            # Also, see comment relating to calculation of CI for relative risk and the
            # retrieval of cell data in the wrong order.
            phjCellValuesList = [item for sublist in phjTempContDF.loc[[phjStratum,phjRiskFactorBaseValue],phjCaseControlValuesList].values.tolist() for item in sublist]
            
            # Calculate SE of natural log of odds ratio.
            # SE of log of OR is calulcated as sqrt(1/a + 1/b + 1/c + 1/d).
            phjLogSE = math.sqrt(sum([1/n for n in phjCellValuesList]))
            
            # Calculate 95% CI.
            # Returned as a list in order of lower limit and upper limit.
            phjRiskFactorCIList = phjCalcCI_lognormal(phjUntransformedPointEstimate = phjTempContDF.loc[phjStratum,phjSuffixDict['oddsratio']],
                                                      phjTransformedSE = phjLogSE,
                                                      phjAlpha = phjAlpha)
            
            # Add 95CI values to dataframe
            # (N.B. The phjCIColsNamesList consists of [or, ci_lower, ci_upper].
            #       Therefore, to put data in correct cells, use list[1] and list[2].
            #       Perhaps I should use a dict.
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[1]] = phjRiskFactorCIList[0]
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[2]] = phjRiskFactorCIList[1]
    
    
    elif phjCIMethod == 'gart':
        # Step through each stratum of the risk factor (except the base value)
        phjRiskFactorStrataList.remove(phjRiskFactorBaseValue)
        for phjStratum in phjRiskFactorStrataList:
            # Create a dictionary containing cells a, b, c and d
            phjCellValuesDict = phjDefineCellValuesDict(phjTempContDF = phjTempContDF,
                                                        phjStratum = phjStratum,
                                                        phjCaseControlValuesList = phjCaseControlValuesList,
                                                        phjRiskFactorBaseValue = phjRiskFactorBaseValue)
            
            # Estimate odds ratio (since at least one of the cell values is zero)
            # (Ref: Morten et al (2011_. Recommended confidence intervals for two independent
            #       binomial proportions. Statistical Methods in Medical Research 0(0) 1–31; see page 14)
            phjTempContDF.loc[phjStratum,phjSuffixDict['oddsratio']] = ( ((phjCellValuesDict['a'] + 0.5) * (phjCellValuesDict['d'] + 0.5)) / ((phjCellValuesDict['b'] + 0.5) * (phjCellValuesDict['c'] + 0.5)) )
            
            # Calculate SE of natural log of relative risk.
            # Adjusted SE of log of RR is calulcated as sqrt( 1/(a + 0.5) + 1/(c + 0.5) - 1/((a+b) + 0.5) - 1/((c+d) + 0.5) ).
            # Alternatively, sqrt( 1/a + 1/c - 1/(a+b) - 1/(c+d))
            phjLogSE = math.sqrt( (1 / (phjCellValuesDict['a'] + 0.5)) +
                               (1 / (phjCellValuesDict['b'] + 0.5)) +
                               (1 / (phjCellValuesDict['c'] + 0.5)) +
                               (1 / (phjCellValuesDict['d'] + 0.5)) )
            
            # Calculate 95% CI
            phjRiskFactorCIList = phjCalcCI_lognormal(phjUntransformedPointEstimate = phjTempContDF.loc[phjStratum,phjSuffixDict['oddsratio']],
                                                      phjTransformedSE = phjLogSE,
                                                      phjAlpha = phjAlpha)
            
            # Add list of 95CI to dataframe
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[1]] = phjRiskFactorCIList[0]
            phjTempContDF.loc[phjStratum,phjCIColsNamesList[2]] = phjRiskFactorCIList[1]
    
    
    else:
        phjTempContDF = phTempContDF
    
    return phjTempContDF



def phjDefineCellValuesDict(phjTempContDF,
                            phjStratum,
                            phjCaseControlValuesList,
                            phjRiskFactorBaseValue):
                                                        
    # The values in the cells that represent a, b, c, and d can't be stored in a list
    # using a list comprehension (as with the odds ratio calculation) because there is
    # a bug in Pandas 0.19.2 and several subsequent releases that caused the 
    # results in the cells to be retrieved in the wrong order; for the OR calculation,
    # the order was not important. This bug was reported to the Pandas GitHub page.
    # Instead, retrieve values from table and allocate to variables named a, b, c, d and
    # then stored in a list
    a = phjTempContDF.loc[phjStratum,phjCaseControlValuesList[0]]
    b = phjTempContDF.loc[phjStratum,phjCaseControlValuesList[1]]
    c = phjTempContDF.loc[phjRiskFactorBaseValue,phjCaseControlValuesList[0]]
    d = phjTempContDF.loc[phjRiskFactorBaseValue,phjCaseControlValuesList[1]]
    
    phjCellValuesDict = {}
    phjCellValuesDict['a'] = a
    phjCellValuesDict['b'] = b
    phjCellValuesDict['c'] = c
    phjCellValuesDict['d'] = d
    
    return phjCellValuesDict



def phjCalcCI_lognormal (phjUntransformedPointEstimate,
                         phjTransformedSE,
                         phjAlpha = 0.05):
    
    # Calculate reliability coefficient
    phjReliabilityCoefficient = norm.ppf(1 - (phjAlpha / 2))
    
    # This function takes an UNTRANSFORMED, log-normally distributed point estimate (e.g. either RR or OR) together with SE of
    # the LOG-TRANSFORMED point estimate and returns a list containing the lower and upper limits of the confidence interval,
    # back-transformed to the origianl scale.
    phjLowerLimit = "{0:.4f}".format(round(math.exp(math.log(phjUntransformedPointEstimate) - phjReliabilityCoefficient*phjTransformedSE),4))
    phjUpperLimit = "{0:.4f}".format(round(math.exp(math.log(phjUntransformedPointEstimate) + phjReliabilityCoefficient*phjTransformedSE),4))
    
    return [phjLowerLimit, phjUpperLimit]



if __name__ == '__main__':
    main()
