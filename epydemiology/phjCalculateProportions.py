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
    pkg_resources.get_distribution('matplotlib')
except pkg_resources.DistributionNotFound:
    matplotlibPresent = False
    print("Error: Matplotlib package not available.")
else:
    matplotlibPresent = True
    import matplotlib.pyplot as plt


try:
    pkg_resources.get_distribution('scipy')
except pkg_resources.DistributionNotFound:
    scipyPresent = False
    print("Error: Scipy package not available.")
else:
    scipyPresent = True
    from scipy.stats import norm


try:
    pkg_resources.get_distribution('statsmodels')
except pkg_resources.DistributionNotFound:
    statsmodelsPresent = False
    print("Error: Statsmodels package not available.")
else:
    statsmodelsPresent = True
    import statsmodels.api as sm
    import statsmodels.stats.proportion as smprop


try:
    pkg_resources.get_distribution('patsy')
except pkg_resources.DistributionNotFound:
    patsyPresent = False
    print("Error: Patsy package not available.")
else:
    patsyPresent = True
    import patsy


import collections
import inspect

from .phjTestFunctionParameters import phjAssert


# ==============
# Main functions
# ==============
#
# Calculate binomial proportions
# ------------------------------
# This function calculates the binomial proportions for a series of binomial variables
# for each level of a given group variable. The dataframe has the following format:
#
#         group     A    B    C
#     0      g1   yes   no  yes
#     1      g1   yes  NaN  yes
#     2      g2    no  NaN  yes
#     3      g1    no  yes  NaN
#     4      g2    no  yes   no
#     5      g2    no  yes  yes
#     6      g1    no  yes  yes
#     7      g1   yes   no  yes
#     8      g2   NaN   no   no
#     9      g1   yes   no   no
#
#  ...and produces the following dataframe:
#
#     group   var   count   success   propn
#        g1     A       6         4    0.66
#        g1     B       5         2    0.40
#        g1     C       5         4    0.80
#        g2     A       3         0    0.00
#        g2     B       4         2    0.50
#        g2     C       4         2    0.50
 
def phjCalculateBinomialProportions(phjDF,
                                    phjColumnsList,
                                    phjSuccess = 'yes',
                                    phjGroupVarName = None,
                                    phjMissingValue = 'missing',
                                    phjBinomialConfIntMethod = 'normal',
                                    phjAlpha = 0.05,
                                    phjPlotProportions = True,
                                    phjGroupsToPlotList = None,
                                    phjSortProportions = False,
                                    phjGraphTitle = None,
                                    phjPrintResults = False):
 
    # Check whether required parameters have been set to correct type and are set to
    # allowable values. N.B. isinstance() can take a tuple to test against multiple types.
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        
        # If phjColumnsList is actually passed as a string (representing a single column)
        # then convert to a list and check that all columns are included as columns in
        # the dataframe.
        if isinstance(phjColumnsList,str):
            phjColumnsList = [phjColumnsList]
            
        phjAssert('phjColumnsList',phjColumnsList,list,phjMustBePresentColumnList = list(phjDF.columns))
        
        phjAssert('phjSuccess',phjSuccess,(str,int,float))
        
        if phjGroupVarName is not None:
            phjAssert('phjGroupVarName',phjGroupVarName,str,phjMustBePresentColumnList = list(phjDF.columns),phjMustBeAbsentColumnList = phjColumnsList)
        
        # It seems that NaN is still a number and will be included in the assert
        # statement that tests for 'float'.
        phjAssert('phjMissingValue',phjMissingValue,(str,int,float),phjBespokeMessage = "Parameter 'phjMissingValue' needs to be a string or a number (including np.nan).")
        phjAssert('phjBinomialConfIntMethod',phjBinomialConfIntMethod,str,phjAllowedOptions = ['normal','agresti_coull','beta','wilson','jeffreys','binom_test'])
        phjAssert('phjAlpha',phjAlpha,float,phjAllowedOptions = {'min':0.0001,'max':0.9999})
        phjAssert('phjPlotProportions',phjPlotProportions,bool)
         
        if phjGroupsToPlotList is not None:
            if phjGroupsToPlotList != 'all':
                if isinstance(phjGroupsToPlotList,str):
                    phjGroupsToPlotList = [phjGroupsToPlotList]
                
                phjAssert('phjGroupsToPlotList',phjGroupsToPlotList,list,phjBespokeMessage = "Parameter 'phjGroupsToPlotList' needs to be a list or the string value 'all'.")
        
        phjAssert('phjSortProportions',phjSortProportions,(bool,str))
        if isinstance(phjSortProportions,str):
            phjAssert('phjSortProportions',phjSortProportions,str,phjAllowedOptions = ['ascending','ascend','asc','descending','descend','desc'],phjBespokeMessage = "The sorting option ('{0}') is not recognised.".format(phjSortProportions))
            
        if phjGraphTitle is not None:
            phjAssert('phjGraphTitle',phjGraphTitle,str)
        
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
        # Bespoke asserts
        # ---------------
        if (phjGroupVarName is not None) & (phjPlotProportions == True):
            assert phjGroupsToPlotList is not None, "The group variable is defined ('{0}') and a plot of proportions is requested but the groups to plot have not been defined.".format(phjGroupVarName)
        
        if phjGroupVarName is None:
            assert phjGroupsToPlotList is None, "The required groups to plot have been set but the group variable name is undefined."
        
        if (phjGroupVarName is not None) & (phjGroupsToPlotList is not None):
            assert ((phjGroupsToPlotList == 'all') or set(phjGroupsToPlotList).issubset(phjDF[phjGroupVarName].unique())), "Groups to plot do not exist in variable '{0}'.".format(phjGroupVarName)
    
    except AssertionError as e:
        
        phjPropDF = None
        
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
        # Set default suffixes and join strings to create column names
        # to use in output dataframe.
        phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
        
        # Create list of unique group levels. (In the bionomial proportions function,
        # unlike for the multinomial proportions function, the category levels are defined
        # as a list that is passed to the function.)
        # When plotting binomial proportions, the list of groups will be used
        # to determine which groups to plot data for.
        # (N.B. If no group name is given, a default value 'group' is used.)
        # i. Categories
        phjGroupLevelsList = phjGetGroupLevelsList(phjDF = phjDF,
                                                   phjGroupVarName = phjGroupVarName,
                                                   phjPrintResults = phjPrintResults)
        
        # If the groups to plot have been defined then only retain those groups that
        # have been selected and occur in the list of categories in the group variable.
        if isinstance(phjGroupsToPlotList,list):
            phjGroupLevelsList = [c for c in phjGroupsToPlotList if c in phjGroupLevelsList]
        
        
        # Create dataframe consisting of total numbers and number of successes.
        # If no group name is given, this will be of the format:
        # 
        #    category   success     total
        #           A         x         y
        #           B         m         n
        #           C         a         b
        #
        # Otherwise, if the group name is given, then the format will be:
        #
        #    group   category   success     total
        #       g1          A         x         y
        #       g1          B         m         n
        #       g1          C         a         b
        #       g2          A         c         d
        #       g2          B         v         w
        #       g2          C         i         j
        
        if phjGroupVarName is None:
            # If no group var name is supplied then calculate success for
            # whole columns and return summary dataframe.
            phjPropDF = phjCountSuccesses(x = phjDF[phjColumnsList],
                                          phjColumnsList = phjColumnsList,
                                          phjSuccessValue = phjSuccess,
                                          phjMissingValue = phjMissingValue)
        
        else:
            # Copy required columns to new dataframe
            phjDF = phjDF[phjColumnsList + [phjGroupVarName]].copy()
            
            # Calculate number of successes for each level of group variable and return summary dataframe
            phjPropDF = phjDF.groupby(phjGroupVarName).apply(lambda x: phjCountSuccesses(x,
                                                                                         phjColumnsList = phjColumnsList,
                                                                                         phjSuccessValue = phjSuccess,
                                                                                         phjMissingValue = phjMissingValue))
        
        # Calculate confidence intervals
        phjPropDF = phjCalculateBinomialConfInts(phjDF = phjPropDF,
                                                 phjSuccVarName = phjSuffixDict['numbersuccesses'],
                                                 phjTotalVarName = phjSuffixDict['numbertrials'],
                                                 phjBinomialConfIntMethod = phjBinomialConfIntMethod,
                                                 phjAlpha = phjAlpha,
                                                 phjPrintResults = phjPrintResults)
        
        
        # Convert long to wide format based on group membership.
        # This is only necessary if more than one group is present.
#        if (phjGroupVarName is not None) & (len(phjPropDF[phjGroupVarName].unique()) > 1):
        if (phjGroupVarName is not None):
            phjPropDF = phjPropDF.unstack(level = 0)
            phjPropDF = phjPropDF.swaplevel(i = -1, j = 0, axis = 1)
            
            # Flatten dataframe multi-index columns to be the following format:
            #    groupName_columnHeading
            # This only needs to be done if there are 2 or more groups. If only one group,
            # then column index is already a single dimension and doesn't need to be flattend.
            phjColIndexNames = pd.Index([phjSuffixDict['joinstr'].join([c[0],c[1]]) for c in phjPropDF.columns.tolist()])
            phjPropDF.columns = phjColIndexNames
            
            # Order columns so all those related to a single group occur together
            phjPropDF = phjPropDF.sort_index(axis = 1)
            
        
        # Sort proportions if requested.
        # (May move to separate function in future.)
        # Proportions can only be sorted if there are no groups to deal with or if only
        # a single group is requested; groups with multiple levels could make sorting
        # proportions confusing.
        # The phjSortProportions variable can be set to a boolean value (True or False) or
        # a string to indicate whether sorting should be ascending or descending.
        if (phjSortProportions != False):
            if (phjGroupVarName is None):
                if (phjSortProportions == True) or (phjSortProportions in ['ascending','ascend','asc']):
                    phjPropDF = phjPropDF.sort_values(by = phjSuffixDict['proportion'],
                                                      axis = 0,
                                                      ascending = True)
                
                elif phjSortProportions in ['descending','descend','desc']:
                    phjPropDF = phjPropDF.sort_values(by = phjSuffixDict['proportion'],
                                                      axis = 0,
                                                      ascending = False)
                
                else:
                    # This message should never be given.
                    print('Option for sorting does not exist. (This message should never be given.)')
            
            else:
                # If group variable is named and the list of groups to plot is only one
                # item long then sort on that single group.
                if isinstance(phjGroupsToPlotList,list):
                    if len(phjGroupsToPlotList) == 1:
                        if (phjSortProportions == True) or (phjSortProportions in ['ascending','ascend','asc']):
                            phjPropDF = phjPropDF.sort_values(by = phjSuffixDict['joinstr'].join([phjGroupsToPlotList[0],phjSuffixDict['proportion']]),
                                                              axis = 0,
                                                              ascending = True)
                        
                        elif phjSortProportions in ['descending','descend','desc']:
                            phjPropDF = phjPropDF.sort_values(by = phjSuffixDict['joinstr'].join([phjGroupsToPlotList[0],phjSuffixDict['proportion']]),
                                                              axis = 0,
                                                              ascending = False)
                        
                        else:
                            # This message should never be given.
                            print('Option for sorting does not exist. (This message should never be given.)')
        
        if phjPrintResults == True:
            with pd.option_context('display.float_format','{:,.4f}'.format):
                print(phjPropDF)
        
        # Plot bar chart of relative frequencies
        if phjPlotProportions == True:
            
            # Plot chart
            phjPlotProportionsBarChart(phjDF = phjPropDF,
                                       phjCategoriesToPlotList = phjColumnsList,
                                       phjGroupVarName = phjGroupVarName,
                                       phjGroupLevelsList = phjGroupLevelsList,
                                       phjAlpha = phjAlpha,
                                       phjGraphTitle = None,
                                       phjXAxisTitle = 'Categories',
                                       phjYAxisTitle = 'Proportions',
                                       phjPrintResults = True)
    
    finally:
        return phjPropDF
 
 
 
# Calculates relative frequencies and multinomial confidence intervals
# --------------------------------------------------------------------
# This function calculates proportions, simultaneous confidence intervals for a categorical
# variable and plots bar charts with asymmetrical error bars.
 
def phjCalculateMultinomialProportions(phjDF,
                                       phjCategoryVarName,
                                       phjGroupVarName = None,
                                       phjMissingValue = 'missing',
                                       phjMultinomialConfIntMethod = 'goodman',
                                       phjAlpha = 0.05,
                                       phjPlotRelFreq = True,
                                       phjCategoriesToPlotList = 'all',
                                       phjGroupsToPlotList = None,   # Currently not implemented
                                       phjGraphTitle = None,
                                       phjPrintResults = False):
    
    # Check whether required parameters have been set to correct type and are set to
    # allowable values. N.B. isinstance() can take a tuple to test against multiple types.
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjCategoryVarName',phjCategoryVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjGroupVarName is not None:
            phjAssert('phjGroupVarName',phjGroupVarName,str,phjMustBePresentColumnList  = list(phjDF.columns))
        
        phjAssert('phjMissingValue',phjMissingValue,(str,int,float),phjBespokeMessage = "Parameter 'phjMissingValue' needs to be a string or a number (including np.nan).")
        phjAssert('phjMultinomialConfIntMethod',phjMultinomialConfIntMethod,str,phjAllowedOptions = ['goodman','sison-glaz'])
        phjAssert('phjAlpha',phjAlpha,float,phjAllowedOptions = {'min':0.0001,'max':0.9999})
        phjAssert('phjPlotRelFreq',phjPlotRelFreq,bool)
        
        if phjCategoriesToPlotList != 'all':
            if isinstance(phjCategoriesToPlotList,str):
                phjCategoriesToPlotList = [phjCategoriesToPlotList]
            
            phjAssert('phjCategoriesToPlotList',phjCategoriesToPlotList,list,phjBespokeMessage = "Parameter 'phjCategoriesToPlotList' needs to be a list or the string value 'all'.")
        
        if phjGroupsToPlotList is not None:
            if phjGroupsToPlotList != 'all':
                if isinstance(phjGroupsToPlotList,str):
                    phjGroupsToPlotList = [phjGroupsToPlotList]
                
                phjAssert('phjGroupsToPlotList',phjGroupsToPlotList,list,phjBespokeMessage = "Parameter 'phjGroupsToPlotList' needs to be a list or the string value 'all'.")
        
        phjAssert('phjGraphTitle',phjGraphTitle,str)
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
    except AssertionError as e:
        
        phjRelFreqDF = None
        
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
        
        # Set default suffixes and join strings to create column names
        # to use in output dataframe.
        phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
        
        # Copy required columns to dataframe and delete rows with missing values
        phjDF = phjKeepRequiredData(phjDF = phjDF,
                                    phjColumnsList = [phjCategoryVarName],
                                    phjGroupVarName = phjGroupVarName,
                                    phjMissingValue = phjMissingValue)
        
        # Create lists of unique category and group levels
        # (N.B. If no group name is given, a default value 'group' is used.)
        # i. Categories
        phjCategoryLevelsList = phjGetCategoryLevelsList(phjDF = phjDF,
                                                         phjCategoryVarName = phjCategoryVarName,
                                                         phjPrintResults = phjPrintResults)
        
        # ii. Groups
        phjGroupLevelsList = phjGetGroupLevelsList(phjDF = phjDF,
                                                   phjGroupVarName = phjGroupVarName,
                                                   phjPrintResults = phjPrintResults)
        
        
        # Create empty dataframe (no columns) with index consisting of all category levels
        phjRelFreqDF = pd.DataFrame(index = phjCategoryLevelsList)
        
        
        # Define which suffix indicates normalization of value_counts() function
        # (i.e. which is absolute counts and which is relative frequency):
        phjSuffixNormOrderedDict = collections.OrderedDict()
        phjSuffixNormOrderedDict[phjSuffixDict['absfreq']] = False
        phjSuffixNormOrderedDict[phjSuffixDict['proportion']] = True
        
        
        # Create temporary dataframes consisting of output from value_counts() function
        # applied to slices of dataframe based on group levels
        for phjSuffix, phjNormalize in phjSuffixNormOrderedDict.items():
            
            # Calculate frequencies and relative frequencies for each group
            if phjGroupVarName is None:
                phjTempRelFreqDF = pd.DataFrame(phjDF[phjCategoryVarName].value_counts(normalize = phjNormalize))
                phjTempRelFreqDF = phjTempRelFreqDF.rename(columns = {phjCategoryVarName: phjSuffix})
                
                # Use non-normalized data to calculate simultaneous confidence intervals
                if phjNormalize == False:
                    phjTempRelFreqDF = phjCalculateMultinomialConfInts(phjDF = phjTempRelFreqDF,
                                                                       phjAbsFreqColumnName = phjSuffix,
                                                                       phjSimultConfIntColumnName = phjSuffixDict['cisuffix'],
                                                                       phjMultinomialConfIntMethod = phjMultinomialConfIntMethod,
                                                                       phjAlpha = phjAlpha,
                                                                       phjPrintResults = phjPrintResults)
                
                # Join temporary data frame to complete dataframe based on index value.
                phjRelFreqDF = phjRelFreqDF.join(phjTempRelFreqDF)
                
                # Cells in summary dataframe with missing values are converted to zero
                # (N.B. In this bit (when phjGroupVarName is None) the following may not be required
                # but I haven't confirmed that for certain so have included it anyway.)
                phjRelFreqDF = phjRelFreqDF.fillna(0)
            
            
            else:
                for phjGroup in phjGroupLevelsList:
                    phjTempRelFreqDF = pd.DataFrame(phjDF.loc[phjDF[phjGroupVarName] == phjGroup,phjCategoryVarName].value_counts(normalize = phjNormalize))
                    phjTempRelFreqDF = phjTempRelFreqDF.rename(columns = {phjCategoryVarName: phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffix])})
                    
                    # Use non-normalized data to calculate simultaneous confidence intervals
                    if phjNormalize == False:
                        phjTempRelFreqDF = phjCalculateMultinomialConfInts(phjDF = phjTempRelFreqDF,
                                                                           phjAbsFreqColumnName = phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffix]),
                                                                           phjSimultConfIntColumnName = phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix']]),
                                                                           phjMultinomialConfIntMethod = phjMultinomialConfIntMethod,
                                                                           phjAlpha = phjAlpha,
                                                                           phjPrintResults = phjPrintResults)
                    
                    
                    # Join temporary data frame to complete dataframe based on index value.
                    phjRelFreqDF = phjRelFreqDF.join(phjTempRelFreqDF)
                
                # Cells in summary dataframe with missing values are converted to zero
                phjRelFreqDF = phjRelFreqDF.fillna(0)
        
        
        
        phjRelFreqDF = phjReorderCols(phjDF = phjRelFreqDF,
                                      phjGroupVarName = phjGroupVarName,
                                      phjGroupLevelsList = phjGroupLevelsList,
                                      phjAlpha = phjAlpha,
                                      phjPrintResults = False)
        
        if phjPrintResults == True:
            print(phjRelFreqDF)
        
        
        # Plot bar chart of relative frequencies
        if phjPlotRelFreq == True:
            
            # Plot chart
            phjPlotProportionsBarChart(phjDF = phjRelFreqDF,
                                       phjCategoriesToPlotList = phjCategoriesToPlotList,
                                       phjGroupVarName = phjGroupVarName,
                                       phjGroupLevelsList = phjGroupLevelsList,
                                       phjAlpha = phjAlpha,
                                       phjGraphTitle = phjGraphTitle,
                                       phjXAxisTitle = phjCategoryVarName,
                                       phjYAxisTitle = 'Relative frequency',
                                       phjPrintResults = False)
    
    finally:
        
        return phjRelFreqDF
 
 
 
def phjCalculateBinomialConfInts(phjDF,
                                 phjSuccVarName = None,
                                 phjFailVarName = None,
                                 phjTotalVarName = None,
                                 phjBinomialConfIntMethod = 'normal',
                                 phjAlpha = 0.05,
                                 phjPrintResults = False):
    
    # Deep copy dataframe to ensure columns not added to passed dataframe
    phjDF = phjDF.copy(deep = True)
    
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Check whether function parameters have been set to correct type and are of
    # correct values.
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        
        if phjSuccVarName is not None:
            #assert isinstance(phjSuccVarName,str), "Parameter 'phjSuccVarName' needs to be a string."
            phjAssert('phjSuccVarName',phjSuccVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjFailVarName is not None:
            #assert isinstance(phjFailVarName,str), "Parameter 'phjFailVarName' needs to be a string."
            phjAssert('phjFailVarName',phjFailVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjTotalVarName is not None:
            #assert isinstance(phjTotalVarName,str), "Parameter 'phjTotalVarName' needs to be a string."
            phjAssert('phjTotalVarName',phjTotalVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        phjAssert('phjBinomialConfIntMethod',phjBinomialConfIntMethod,str,phjAllowedOptions = ['normal','agresti_coull','beta','wilson','jeffreys','binom_test'])
        phjAssert('phjAlpha',phjAlpha,float,phjAllowedOptions = {'min':0.0001,'max':0.9999})
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
        # Bespoke asserts
        # ---------------
        # The user can enter two of three parameters in list of successes, failures or total.
        # Check that at least 2 parameters are entered.
        nArgs = len([i for i in [phjSuccVarName,phjFailVarName,phjTotalVarName] if i is not None])
        assert nArgs >= 2, "At least 2 variables from phjSuccVarName, phjFailVarName and phjTotalVarName need to be entered but only {} has been entered.".format(nArgs)
        
        # If all three parameters have been entered, check that successes + failures = total
        if nArgs == 3:
            assert (phjDF[phjSuccVarName] + phjDF[phjFailVarName]).equals(phjDF[phjTotalVarName]), "The '{0}' and '{1}' columns do not add up to the values in the '{2}' column.".format(phjSuccVarName,phjFailVarName,phjTotalVarName)
        
        # New columns
        # Some new column names will be created.
        phjProbName = phjSuffixDict['proportion']
        phjProbCILowLimName = phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])
        phjProbCIUppLimName = phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])
        phjProbCILowIntName = phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowint']])
        phjProbCIUppIntName = phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciuppint']])
        
        # Check that new column names do not already exist
        phjAssert('New column names',
                  [phjProbName,phjProbCILowLimName,phjProbCIUppLimName,phjProbCILowIntName,phjProbCIUppIntName],
                  list,
                  phjMustBeAbsentColumnList = list(phjDF.columns))
    
    except AssertionError as e:
        
        phjDF = None
        
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
        # Calculations are made using successes and totals.
        # If 2 column names entered and 1 is failures then calculate either the successes or the totals column.
        if (nArgs == 2) & (phjFailVarName is not None):
            if phjSuccVarName is None:
                phjSuccVarName = phjSuffixDict['numbersuccess']
                phjDF[phjSuccVarName] = phjDF[phjTotalVarName] - phjDF[phjFailVarName]
            elif phjTotalVarName is None:
                phjTotalVarName = phjSuffixDict['numbertrials']
                phjDF[phjTotalVarName] = phjDF[phjSuccVarName] + phjDF[phjFailVarName]
 
        # Ensure count data is stored as integer values. Otherwise,
        # for some reason, calculations with object columns can go awry.
        phjDF[phjSuccVarName] = phjDF[phjSuccVarName].astype(int)
        phjDF[phjTotalVarName] = phjDF[phjTotalVarName].astype(int)
 
        # Calculate proportions
        phjDF[phjProbName] = phjDF[phjSuccVarName] / phjDF[phjTotalVarName]
 
        # Get binomial confidence intervals
        phjBinomConfIntArr = smprop.proportion_confint(count = phjDF[phjSuccVarName],
                                                       nobs = phjDF[phjTotalVarName],
                                                       alpha = phjAlpha,
                                                       method = phjBinomialConfIntMethod)
 
        phjDF[phjProbCILowLimName] = [i for i in phjBinomConfIntArr[0]]
        phjDF[phjProbCIUppLimName] = [i for i in phjBinomConfIntArr[1]]
        
        phjDF[phjProbCILowIntName] = phjDF[phjProbName] - phjDF[phjProbCILowLimName]
        phjDF[phjProbCIUppIntName] = phjDF[phjProbCIUppLimName] - phjDF[phjProbName]
        
    finally:
        if phjPrintResults == True:
            print('Final dataframe\n')
            with pd.option_context('display.max_rows',6, 'display.max_columns',8):
                print(phjDF)
            print('\n')
        
        return phjDF
 
 
 
def phjSummaryTableToBinaryOutcomes(phjDF,
                                    phjVarsToIncludeList,
                                    phjSuccVarName = None,
                                    phjFailVarName = None,
                                    phjTotalVarName = None,
                                    phjOutcomeVarName = 'outcome',
                                    phjPrintResults = False):
    
    # This function takes a table of counted binary results and converts it
    # to a dataframe of binary outcomes, ready for logistic regression.
    # (This is useful if the function used to do logistic regression does not
    # include a frequency weight option.)
    
    # Check whether function parameters have been set to correct type and are of
    # correct values.
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjVarsToIncludeList',phjVarsToIncludeList,(str,list),phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjSuccVarName is not None:
            phjAssert('phjSuccVarName',phjSuccVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjFailVarName is not None:
            phjAssert('phjFailVarName',phjFailVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjTotalVarName is not None:
            phjAssert('phjTotalVarName',phjTotalVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        phjAssert('phjOutcomeVarName',phjOutcomeVarName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
        # Bespoke asserts
        # ---------------
        # The user can enter two of three parameters in list of successes, failures or total.
        # Check that at least 2 parameters are entered.
        nArgs = len([i for i in [phjSuccVarName,phjFailVarName,phjTotalVarName] if i is not None])
        assert nArgs >= 2, "At least 2 variables from phjSuccVarName, phjFailVarName and phjTotalVarName need to be entered but only {} has been entered.".format(nArgs)
        
        # If all three parameters have been entered, check that successes + failures = total
        if nArgs == 3:
            assert (phjDF[phjSuccVarName] + phjDF[phjFailVarName]).equals(phjDF[phjTotalVarName]), "The '{0}' and '{1}' columns do not add up to the values in the '{2}' column.".format(phjSuccVarName,phjFailVarName,phjTotalVarName)
    
    except AssertionError as e:
        
        phjDF = None
        
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
        # Set default suffixes and join strings to create column names
        # to use in output dataframe.
        phjSuffixDict = phjDefineSuffixDict()
        
        # Calculations are made using successes and failures.
        # If 2 column names entered and 1 is totals then calculate either the successes or the failures column.
        if (nArgs == 2) & (phjTotalVarName is not None):
            if phjSuccVarName is None:
                phjSuccVarName = phjSuffixDict['numbersuccesses']
                phjDF[phjSuccVarName] = phjDF[phjTotalVarName] - phjDF[phjFailVarName]
            
            elif phjFailVarName is None:
                phjFailVarName = phjSuffixDict['numberfailures']
                phjDF[phjFailVarName] = phjDF[phjTotalVarName] - phjDF[phjSuccVarName]
        
        
        # If the list of variables to include is only a single variable included as a string,
        # convert to a list before going any further.
        if isinstance(phjVarsToIncludeList,str):
            phjVarsToIncludeList = [phjVarsToIncludeList]
        
        # Make sure the success and failure variables are not included in the list of
        # variables to include. It's OK if they are because this line will correct for it.
        phjVarsToIncludeList = [i for i in phjVarsToIncludeList if i not in [j for j in [phjSuccVarName,phjFailVarName,phjTotalVarName] if j is not None]]
        
        if phjPrintResults == True:
            print('Initial dataframe\n')
            print(phjDF.loc[:,phjVarsToIncludeList + [j for j in [phjSuccVarName,phjFailVarName,phjTotalVarName] if j is not None]])
            print('\n')
            
        
        # Stack positive (success) and negative (failure) results one on top of the other
        phjDF = phjDF.melt(id_vars = phjVarsToIncludeList,
                                   value_vars = [phjSuccVarName,phjFailVarName],
                                   var_name = phjOutcomeVarName,
                                   value_name = 'count').reset_index(drop = True)
        
        phjDF = phjDF.loc[phjDF.index.repeat(phjDF['count'])]
        
        phjDF[phjOutcomeVarName] = phjDF[phjOutcomeVarName].replace({phjSuccVarName: 1,
                                                                     phjFailVarName: 0})
        
        phjDF = phjDF[[x for x in phjDF.columns if x != 'count']].reset_index(drop = True)
        
    finally:
        if phjPrintResults == True:
            print('Final dataframe\n')
            with pd.option_context('display.max_rows',6, 'display.max_columns',2):
                print(phjDF)
            print('\n')
        
        return phjDF
 
 
 
def phjAnnualDiseaseTrend(phjDF,
                          phjYearVarName,
                          phjPositivesVarName = None,
                          phjNegativesVarName = None,
                          phjTotalVarName = None,
                          phjConfIntMethod = 'normal',
                          phjAlpha = 0.05,
                          phjPlotProportions = True,
                          phjPlotPrediction = True,
                          phjGraphTitleStr = None,
                          phjPrintResults = False):
    
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Check whether required parameters have been set to correct type
    # and check whether arguments are set to allowable values.
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjYearVarName',phjYearVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        if phjPositivesVarName is not None:
            phjAssert('phjPositivesVarName',phjPositivesVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
            
        if phjNegativesVarName is not None:
            phjAssert('phjNegativesVarName',phjNegativesVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
            
        if phjTotalVarName is not None:
            phjAssert('phjTotalVarName',phjTotalVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
            
        phjAssert('phjConfIntMethod',phjConfIntMethod,str,phjAllowedOptions = ['normal','agresti_coull','beta','wilson','jeffreys','binom_test'])
        phjAssert('phjAlpha',phjAlpha,float,phjAllowedOptions = {'min':0.0001,'max':0.9999})
        phjAssert('phjPlotProportions',phjPlotProportions,bool)
        phjAssert('phjPlotPrediction',phjPlotPrediction,bool)
        
        if phjGraphTitleStr is not None:
            phjAssert('phjGraphTitleStr',phjGraphTitleStr,str)
        
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
        # Bespoke asserts
        # ---------------
        # The user can enter two of three parameters in list of successes, failures or total.
        # Check that at least 2 parameters are entered.
        nArgs = len([i for i in [phjPositivesVarName,phjNegativesVarName,phjTotalVarName] if i is not None])
        assert nArgs >= 2, "At least 2 variables from phjPositivesVarName, phjNegativesVarName and phjTotalVarName need to be entered but only {} has been entered.".format(nArgs)
        
        # If all three parameters have been entered, check that successes + failures = total
        if nArgs == 3:
            assert (phjDF[phjPositivesVarName] + phjDF[phjNegativesVarName]).equals(phjDF[phjTotalVarName]), "The '{0}' and '{1}' columns do not add up to the values in the '{2}' column.".format(phjPositivesVarName,phjNegativesVarName,phjTotalVarName)
        
        
        # New columns
        # Some new column names will be created. Some columns will contain information
        # relating to binomial confidence intervals; any assert errors in the names of
        # these columns will be handed by phjCalculateBinomialConfInts(). However, some
        # columns will be created by this function relating to predicted probabilities
        # and associated confidence intervals; assertion error in these names need to be
        # addressed here.
        
        phjProbName = phjSuffixDict['proportion']
        #phjProbCILowLimName is not used in this function but is created by phjCalculateBinomialConfInts
        #phjProbCIUppLimName is not used in this function but is created by phjCalculateBinomialConfInts
        phjProbCILowIntName = phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowint']])   # Created by phjCalculateBinomialConfInts
        phjProbCIUppIntName = phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciuppint']])   # Created by phjCalculateBinomialConfInts
        
        # N.B. Also a column called 'Intercept' will be created by patsy
        phjPredProbName = ''.join([phjSuffixDict['predicted'],phjSuffixDict['probability']])
        phjPredProbSEName = phjSuffixDict['joinstr'].join([phjPredProbName,phjSuffixDict['stderr']])
        phjPredProbCILowLimName = phjSuffixDict['joinstr'].join([phjPredProbName,phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])
        phjPredProbCIUppLimName = phjSuffixDict['joinstr'].join([phjPredProbName,phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])
        
        phjAssert('New column names',
                  [phjProbName,'Intercept',phjPredProbName,phjPredProbSEName,phjPredProbCILowLimName,phjPredProbCIUppLimName],
                  list,
                  phjMustBeAbsentColumnList = list(phjDF.columns))
    
    except AssertionError as e:
        
        phjPropDF = None
        
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
        try:
            # Try to calculate binomial confidence intervals
            phjPropDF = phjCalculateBinomialConfInts(phjDF = phjDF,
                                                     phjSuccVarName = phjPositivesVarName,
                                                     phjFailVarName = phjNegativesVarName,
                                                     phjTotalVarName = phjTotalVarName,
                                                     phjBinomialConfIntMethod = phjConfIntMethod,
                                                     phjAlpha = phjAlpha,
                                                     phjPrintResults = phjPrintResults)
            
            # Try to convert to table of binary outcomes
            phjLongDF = phjSummaryTableToBinaryOutcomes(phjDF = phjPropDF,
                                                        phjVarsToIncludeList = [phjYearVarName],
                                                        phjSuccVarName = phjPositivesVarName,
                                                        phjFailVarName = phjNegativesVarName,
                                                        phjTotalVarName = phjTotalVarName,
                                                        phjOutcomeVarName = phjSuffixDict['outcome'],
                                                        phjPrintResults = False)
        
        except AssertionError as e:
            
            phjPropDF = None
            
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
            #import pdb; pdb.set_trace()
            
            # Logistic regression model
            phjFormulaStr = '{} ~ {}'.format(phjSuffixDict['outcome'],phjYearVarName)
            
            # Calculating post-estimation using matrices
            y, X = patsy.dmatrices(formula_like = phjFormulaStr,
                                   data = phjLongDF,
                                   NA_action = 'drop',
                                   return_type = 'dataframe')
            
            model = sm.Logit(endog = y,
                             exog = X,
                             missing = 'drop').fit()
            
            if phjPrintResults == True:
                print(model.summary2())
                print('\n')
            else:
                model.summary2()    # It seems that the .summary2() method needs to be run even if not printed, otherwise an error occurs.
            
            # Calculate predicted probabilities
            X[phjPredProbName] = model.predict() # predicted probability
            
            # Estimate confidence interval for predicted probabilities using Delta method
            # This method is taken from an answer by David Dale on StackOverflow (see https://stackoverflow.com/questions/47414842/confidence-interval-of-probability-prediction-from-logistic-regression-statsmode/47419474).
            cov = model.cov_params()
            gradient = (X[phjPredProbName] * (1 - X[phjPredProbName]) * X[[x for x in X if x != phjPredProbName]].T).T.values # matrix of gradients for each observation
            
            # Add column containing SE of predicted probabilities
            X[phjPredProbSEName] = [np.sqrt(np.dot(np.dot(g, cov), g)) for g in gradient]
            
            # Add column containing CI lower and upper limits
            # The format of ci_limit = np.maximum(0, np.minimum(1, prob + std_errors * c)) ensures limit lies between 0 and 1.
            # Multiplier for standard error calculated as:
            #     norm.ppf(.025) = -1.960063984540054
            #     norm.ppf(.975) = 1.959963984540054
            
            # Calculate confidence intervals. The max(0,min(1,interval)) construct ensures that
            # the interval does not extend beyond 1 or 0. Again this was taken from the answer
            # by David Dale on StackOverflow (see https://stackoverflow.com/questions/47414842/confidence-interval-of-probability-prediction-from-logistic-regression-statsmode/47419474).
            # Lower interval
            X[phjPredProbCILowLimName] = np.maximum(0,np.minimum(1,X[phjPredProbName] + (norm.ppf(phjAlpha/2) * X[phjPredProbSEName])))   # N.B. The norm.pdf(0.025) is negative therefore equates to mean minus interval.
            # Upper interval
            X[phjPredProbCIUppLimName] = np.maximum(0,np.minimum(1,X[phjPredProbName] + (norm.ppf(1 - (phjAlpha/2)) * X[phjPredProbSEName])))
            
            # Keep only a single value for each group
            X = X.drop_duplicates(keep = 'first')
            
            # Join predicted probabilities with original dataframe
            phjPropDF = phjPropDF.merge(right = X,
                                        left_on = phjYearVarName,
                                        right_on = phjYearVarName)
            
            #if phjPrintResults == True:
            #    print(phjPropDF)
            #    print('\n')
            
            # Plot actual proportion as barchart and predicted probabilities as line
            if (phjPlotProportions == True) | (phjPlotPrediction == True):
                
                fig = plt.figure(figsize = (10,6))
                ax = fig.add_subplot(111)
                
                if phjPlotProportions == True:
                    rects = ax.bar(phjPropDF[phjYearVarName],
                                   phjPropDF[phjProbName],
                                   yerr = [phjPropDF[phjProbCILowIntName],
                                           phjPropDF[phjProbCIUppIntName]],
                                   capsize = 4)
                
                if phjPlotPrediction == True:
                    # Only plot trend line if logistic regression model converge. Otherwise, just plot bars.
                    if model.mle_retvals['converged']:
                        # Plot pred prob
                        pprobline = ax.plot(phjPropDF[phjYearVarName],
                                            phjPropDF[phjPredProbName],
                                            linestyle = 'solid',
                                            color = 'green')
                        
                        # Plot lower limit of ci for pred prob
                        pprobllimline = ax.plot(phjPropDF[phjYearVarName],
                                                phjPropDF[phjPredProbCILowLimName],
                                                linestyle = 'dashed',
                                                color = 'red')
                        
                        # Plot upper limit of ci for pred prob
                        pprobulimline = ax.plot(phjPropDF[phjYearVarName],
                                                phjPropDF[phjPredProbCIUppLimName],
                                                linestyle = 'dashed',
                                                color = 'red')
                        
                        phjText = "Trend line p-value = {0:.4f}".format(model.pvalues[phjYearVarName])
                    
                    else:
                        phjText = "Logistic regression model failed to converge"
                    
                    # Add p value for logistic regression model (or failure-to-converge notice)
                    ax.text(ax.get_xlim()[1],
                            ax.get_ylim()[1],
                            phjText,
                            horizontalalignment = 'right',
                            verticalalignment = 'bottom')
                
                ax.set_xlabel(phjYearVarName)
                ax.set_ylabel('Proportion / probability')
                ax.set_title(phjGraphTitleStr)
                
                major_xticks = phjPropDF[phjYearVarName].tolist()
                ax.set_xticks(major_xticks, minor = False)
                
                plt.show()
        
    finally:
        
        return phjPropDF
 
 
 
# ====================
# Supporting functions
# ====================
 
def phjDefineSuffixDict(phjAlpha = 0.05):
 
    # Define abbreviation for confidence interval
    phjCIAbbrev = 'CI'
 
    # Create a dict containing all the default suffixes and join strings that will be used to facilitate
    # passing information from one function to the next.
    # The names used for calculated confidence intervals of RR and OR are taken from:
    # Morten et al (2011_. Recommended confidence intervals for two independent
    # binomial proportions. Statistical Methods in Medical Research 0(0) 1–31)
    phjSuffixDict = {'joinstr':'_',                                    # Character to join name and suffix
                     'numbersuccesses':'success',                      # Number of successes (used to calculate binomial proportions)
                     'numberfailures':'failure',                       # Number of failures
                     'numbertrials':'obs',                             # Number of trials (used to calculate binomial proportions)
                     'absfreq':'count',                                # Absolute frequency suffix (used to calcuate multinomial proportions)
                     'proportion':'prop',                              # Relative frequency suffix (used to calcuate multinomial proportions)
                     'probability':'prob',                             # Probability suffix
                     'predicted':'pred',                               # Used as suffix for predicted parameters
                     'totalnumber':'total',                            # Total number (e.g. cases plus controls)
                     'outcome':'outcome',                              # Name of outcome variable
                     'cisuffix':phjCISuffix(phjAlpha,phjCIAbbrev),     # Confidence interval suffix
                     'cilowlim':'llim',                                # lower limit of confidence interval
                     'ciupplim':'ulim',                                # upper limit of confidence interval
                     'cilowint':'lint',                                # lower interval for confidence interval
                     'ciuppint':'uint',                                # upper interval for confidence interval
                     'woolf':'woolf',                                  # Used to describe Woolf confidence interval of OR
                     'gart':'gart',                                    # Used to describe Gart confidence interval of OR
                     'katz':'katz',                                    # Used to describe Katz confidence interval of RR
                     'kooperman':'kooperman',                          # Used to describe Kooperman confidence interval of RR
                     'adj_log':'adj_log',                              # Used to estimate CI for relative risk is cells contain zero
                     'risk':'risk',                                    # Risk suffix
                     'relrisk':'rr',                                   # Relative risk suffix
                     'odds':'odds',                                    # Odds suffix
                     'logodds':'logodds',                              # Log odds suffix
                     'oddsratio':'or',                                 # Odds ratio suffix
                     'catmidpoints':'midpoints',                       # Midpoints of categorized continuous variable
                     'categorisedvar':'cat',                           # Suffix to indicate a continuous var had been categorised
                     'stderr':'se'                                     # Standard error
                    }
 
    return phjSuffixDict
 
 
 
def phjCISuffix(phjAlpha,
                phjCIAbbrev):
 
    return (str(int(100 - 100*phjAlpha)) + phjCIAbbrev)
 
 
 
def phjCountSuccesses(x,
                      phjColumnsList,
                      phjSuccessValue = 'yes',
                      phjMissingValue = 'missing'):
 
    # Get a list of the terms used to head columns in summary tables.
    # (The alpha value is not required and can be left as default.)
    phjSuffixDict = phjDefineSuffixDict()
 
    phjSummaryDF = pd.DataFrame(index = phjColumnsList, columns = [phjSuffixDict['numbertrials'],
                                                                   phjSuffixDict['numbersuccesses']])
 
    for var in phjColumnsList:
        phjSummaryDF.loc[var,phjSuffixDict['numbertrials']] = ((x[var].replace(phjMissingValue,np.nan).dropna()) == phjSuccessValue).count()
        phjSummaryDF.loc[var,phjSuffixDict['numbersuccesses']] = ((x[var].replace(phjMissingValue,np.nan).dropna()) == phjSuccessValue).sum()
 
    return phjSummaryDF
 
 
 
def phjKeepRequiredData(phjDF,
                        phjColumnsList,
                        phjGroupVarName = None,
                        phjMissingValue = 'missing'):
 
    # Copy required columns to dataframe
    if phjGroupVarName is not None:
        phjDF = phjDF.loc[:,[phjGroupVarName] + phjColumnsList].copy()
    else:
        phjDF = phjDF.loc[:,phjColumnsList].copy()
 
    # Remove rows with missing values
    phjDF = phjDF.replace(phjMissingValue,np.nan)
    phjDF = phjDF.dropna(axis = 0, how = 'any')
 
    return phjDF
 
 
 
def phjGetCategoryLevelsList(phjDF,
                             phjCategoryVarName = None,
                             phjPrintResults = False):
 
    phjCategoryLevelsList = list(phjDF[phjCategoryVarName].unique())
 
    if phjPrintResults == True:
        print('\nCategory levels: ',phjCategoryLevelsList)
 
    return phjCategoryLevelsList
 
 
 
def phjGetGroupLevelsList(phjDF,
                          phjGroupVarName = None,
                          phjPrintResults = False):
    # This function returns a list of group names that will be used as
    # the stem to label columns in the relative frequency dataframe.
    # Basically, the group names consist of all the levels of the group variable
    # except in cases where no group name is defined (as relative frequencies are
    # returned for the whole dataset) in which case the list consists of a default
    # 'group' item.
    if phjGroupVarName is None:
        phjGroupLevelsList = ['group']
    else:
        phjGroupLevelsList = list(phjDF[phjGroupVarName].unique())
 
    if phjPrintResults == True:
        print('Group levels: ',phjGroupLevelsList,'\n')
 
    return phjGroupLevelsList
 
 
 
def phjCalculateMultinomialConfInts(phjDF,
                                    phjAbsFreqColumnName = None,
                                    phjSimultConfIntColumnName = None,
                                    phjMultinomialConfIntMethod = 'goodman',
                                    phjAlpha = 0.05,
                                    phjPrintResults = False):
 
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
 
    # Get simultaneous confidence intervals
    phjSimultConfIntArr = smprop.multinomial_proportions_confint(phjDF[phjAbsFreqColumnName],
                                                                 alpha = phjAlpha,
                                                                 method = phjMultinomialConfIntMethod)
 
    phjDF[phjSuffixDict['joinstr'].join([phjSimultConfIntColumnName,phjSuffixDict['cilowlim']])] = [i[0] for i in phjSimultConfIntArr]
    phjDF[phjSuffixDict['joinstr'].join([phjSimultConfIntColumnName,phjSuffixDict['ciupplim']])] = [i[1] for i in phjSimultConfIntArr]
 
    return phjDF
 
 
 
def phjReorderCols(phjDF,
                   phjGroupVarName = None,
                   phjGroupLevelsList = None,
                   phjAlpha = 0.05,
                   phjPrintResults = False):
 
    # Get a list of the terms used to head columns in summary tables.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
 
    # Reorder columns
    if phjGroupVarName is None:
        phjColOrder = [phjSuffixDict['absfreq'],
                       phjSuffixDict['proportion'],
                       phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']]),
                       phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])]
 
    else:
        phjColOrder = []
        phjColOrder.extend([phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['absfreq']]) for phjGroup in phjGroupLevelsList])
        phjColOrder.extend([phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['proportion']]) for phjGroup in phjGroupLevelsList])
        phjColOrder.extend([phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix'],phjLimit]) for phjGroup in phjGroupLevelsList for phjLimit in [phjSuffixDict['cilowlim'],phjSuffixDict['ciupplim']]])
 
    phjDF = phjDF[phjColOrder]
 
    return phjDF
 
 
 
def phjPlotProportionsBarChart(phjDF,
                               phjCategoriesToPlotList = 'all',
                               phjGroupVarName = None,
                               phjGroupLevelsList = None,
                               phjAlpha = 0.05,
                               phjGraphTitle = None,
                               phjXAxisTitle = None,
                               phjYAxisTitle = None,
                               phjPrintResults = False):
    # Plot bar chart of relative frequencies for each group at all category levels.
    # The names of the columns to plot consist of the group names and the suffixes (and joining string).
    # The names of the columns to plot are generated using a list comprehension in code below.
    # The legend, however, does not contain the suffix text.
 
    # Get a list of the terms used to head columns in summary tables.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
 
    # Define which categories to plot
    if phjCategoriesToPlotList == 'all':
        # Get a list of all categories from the dataframe index.
        phjIndexItemsToPlot = list(phjDF.index.values)
    else:
        # The following list comprehension ensures that the columns are plotting in the
        # same order in which they appear in the dataframe, regardless of the order in
        # which they were listed by the user.
        phjIndexItemsToPlot = [i for i in list(phjDF.index.values) if i in phjCategoriesToPlotList]
 
 
    if phjGroupVarName is None:                        
        # Calculate y errors
        phjYErrors = phjGetYErrors(phjDF = phjDF,
                                   phjCategoriesToPlotList = phjIndexItemsToPlot,
                                   phjGroupVarName = phjGroupVarName,
                                   phjGroupLevelsList = phjGroupLevelsList,
                                   phjAlpha = phjAlpha,
                                   phjPrintResults = phjPrintResults)
 
        # Plot bar chart of relative frequencies
        ax = phjDF.loc[phjIndexItemsToPlot,
                           phjSuffixDict['proportion']].plot(kind = 'bar',
                                                             title = phjGraphTitle,
                                                             yerr = phjYErrors,
                                                             capsize = 3,
                                                             color = 'blue')
 
    else:
        # Calculate y errors
        phjYErrors = phjGetYErrors(phjDF = phjDF,
                                   phjCategoriesToPlotList = phjIndexItemsToPlot,
                                   phjGroupVarName = phjGroupVarName,
                                   phjGroupLevelsList = phjGroupLevelsList,
                                   phjAlpha = phjAlpha,
                                   phjPrintResults = phjPrintResults)
 
 
        # Plot bar chart of relative frequencies
        ax = phjDF.loc[phjIndexItemsToPlot,
                           [phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['proportion']]) for phjGroup in phjGroupLevelsList]].plot(kind = 'bar',
                                                                                                                                                 title = phjGraphTitle,
                                                                                                                                                 yerr = phjYErrors,
                                                                                                                                                 capsize = 3)
 
    ax.set_ylabel(phjYAxisTitle)
    ax.set_xlabel(phjXAxisTitle)
    ax.legend(labels = phjGroupLevelsList)
 
    return
 
 
 
def phjGetYErrors(phjDF,
                  phjCategoriesToPlotList = None,
                  phjParameterValue = 'proportion',   # This is the value that is plotted (e.g. proportion, logodds etc.)
                  phjGroupVarName = None,
                  phjGroupLevelsList = None,
                  phjAlpha = 0.05,
                  phjPrintResults = False):
 
    # CHECK
    # Check phjParameterValue is a value in the suffix dict keys
 
 
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
 
 
    # The following list comprehension produces a M x 2 x N list which is what is need for
    # asymmetrical error bars. N.B. the '2' bit represents lower interval and upper interval.
    # If there were 4 columns of data across 3 groups, the array would be of the format:
    # [ [[1,1,1,1],[1,1,1,1]],[[1,1,1,1],[1,1,1,1]],[[1,1,1,1],[1,1,1,1]] ]
    #
    # N.B. The single column referred to in .loc[] must not be a list otherwise tolist() will
    # not work e.g. phjDF.loc[['A','B'],'col1'].tolist() works, but
    #               phjDF.loc[['A','B'],['col1']].tolist() does not.
    #
    # Remember, the CI functions produces the lower and upper limits of the CI whereas the
    # error bars plot the intervals between the proportion and the upper and lower limits.
    # Therefore, it is necessary to calculate the difference between proportion and CI limits
    # in order to plot error bars.
 
    if phjGroupVarName is None:
        phjYErrors = [[ (phjDF.loc[phjCategoriesToPlotList,phjSuffixDict[phjParameterValue]] - phjDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])]).tolist(),
                        (phjDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])] - phjDF.loc[phjCategoriesToPlotList,phjSuffixDict[phjParameterValue]]).tolist() ]]
 
    else:
        phjYErrors = [[ (phjDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict[phjParameterValue]])] - phjDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])]).tolist(),
                        (phjDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])] - phjDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict[phjParameterValue]])]).tolist() ] for phjGroup in phjGroupLevelsList]
 
 
    #if phjPrintResults == True:
    #    print("\nErrors:")
    #    print(phjYErrors)
 
    return phjYErrors



if __name__ == '__main__':
    main()
