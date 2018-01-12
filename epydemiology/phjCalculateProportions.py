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


try:
    pkg_resources.get_distribution('statsmodels')
except pkg_resources.DistributionNotFound:
    statsmodelsPresent = False
    print("Error: Statsmodels package not available.")
else:
    statsmodelsPresent = True
    import statsmodels.stats.proportion as smprop


import collections



# ==============
# Main functions
# ==============
#
# Calculate binomial proportions
# ------------------------------
# This function calculates the binomial proportions of a series of binomial variables
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


def phjCalculateBinomialProportions(phjTempDF,
                                    phjColumnsList = None,
                                    phjSuccess = 'yes',
                                    phjGroupVarName = None,
                                    phjMissingValue = 'missing',
                                    phjBinomialConfIntMethod = 'normal',
                                    phjAlpha = 0.05,
                                    phjPlotProportions = True,
                                    phjGroupsToPlotList = 'all',
                                    phjSortProportions = False,
                                    phjGraphTitle = None,
                                    phjPrintResults = False):
    
    # Error checking required:
    # 1. NEED TO CHECK that all variables in var list are in the dataframe.
    # 2. NEED TO CHECK that group var is not included in list of columns
    # 3. IF GROUPS TO PLOT IS A LIST AND GROUP VAR NAME IS NONE THEN CHECK
    
    
    # Set default suffixes and join strings to create column names
    # to use in output dataframe.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)

    
    # Create lists of unique group levels. (In the bionomial proportions function,
    # unlike for the multinomial proportions function, the category levels are defined
    # as a list that is passed to the function.)
    # (N.B. If no group name is given, a default value 'group' is used.)
    # i. Categories
    phjGroupLevelsList = phjGetGroupLevelsList(phjTempDF = phjTempDF,
                                               phjGroupVarName = phjGroupVarName,
                                               phjPrintResults = phjPrintResults)


    
    # Create dataframe consisting of total numbers and number of successes
    if phjGroupVarName is None:
        # If no group var name is supplied then calculate success for
        # whole columns and return summary dataframe.
        phjPropDF = phjCountSuccesses(x = phjTempDF[phjColumnsList],
                                      phjColumnsList = phjColumnsList,
                                      phjMissingValue = phjMissingValue)
    
    else:
        # Copy required columns to new dataframe
        phjTempDF = phjTempDF[phjColumnsList + [phjGroupVarName]].copy()

        # Calculate number of successes for each level of group variable and return summary dataframe
        phjPropDF = phjTempDF.groupby(phjGroupVarName).apply(lambda x: phjCountSuccesses(x,
                                                                                         phjColumnsList = phjColumnsList,
                                                                                         phjMissingValue = phjMissingValue))
    
    
    # Ensure count data is stored as integer values. Otherwise,
    # for some reason, calculations with object columsn can go awry.
    phjPropDF[phjSuffixDict['numbertrials']] = phjPropDF[phjSuffixDict['numbertrials']].astype(int)
    phjPropDF[phjSuffixDict['numbersuccesses']] = phjPropDF[phjSuffixDict['numbersuccesses']].astype(int)
    

    phjPropDF[phjSuffixDict['proportion']] = phjPropDF[phjSuffixDict['numbersuccesses']] / phjPropDF[phjSuffixDict['numbertrials']]


    phjPropDF = phjCalculateBinomialConfInts(phjTempDF = phjPropDF,
                                             phjSuccessesColumnName = phjSuffixDict['numbersuccesses'],
                                             phjNColumnName = phjSuffixDict['numbertrials'],
                                             phjBinomialConfIntMethod = phjBinomialConfIntMethod,
                                             phjAlpha = phjAlpha,
                                             phjPrintResults = phjPrintResults)
    
#    if phjSortProportions != False:
#        if phjSortProportions == 'asc':
#            phjPropDF = phjPropDF.sort_values(by = 'proportion',
#                                              axis = 0,
#                                              ascending = True)
#                                              
#        elif phjSortProportions == 'desc':
#            phjPropDF = phjPropDF.sort_values(by = 'proportion',
#                                              axis = 0,
#                                              ascending = False)
#            
#        else:
#            print('Option for sorting does not exist.')


#    if phjBinomialConfIntMethod == 'normal':
#        # Calculate standard error
#        phjPropDF['stderr'] = ((phjPropDF['proportion'] * (1 - phjPropDF['proportion'])) / phjPropDF['count']).pow(1/2)
#        
#        # Calculate reliability coefficient
#        phjReliabilityCoefficient = norm.ppf(1 - (phjAlpha / 2))
#        
#        # Calculate confidence interval
#        phjCIColumnName = phjCISuffix(phjAlpha)
#        phjPropDF[phjCIColumnName] = phjReliabilityCoefficient * phjPropDF['stderr']
#        
#        # Calculate uppper and lower CI limits
#        phjPropDF['lowCILimit'] = phjPropDF['proportion'] - phjPropDF[phjCIColumnName]
#        phjPropDF['uppCILimit'] = phjPropDF['proportion'] + phjPropDF[phjCIColumnName]
#        
#    else:
#        phjPropDF['stderr'] = np.nan
        
    
    # Convert long to wide format based on group membership.
    # This is only necessary if more than one group is present.
    if phjGroupVarName is not None:
        phjPropDF = phjPropDF.unstack(level = 0)
        phjPropDF = phjPropDF.swaplevel(i = -1, j = 0, axis = 1)
    
    
    # Flatten dataframe multi-index columns to be the following format:
    #    groupName_columnHeading
    # This only needs to be done if there are 2 more groups. If only one group,
    # then column index is already a single dimension and doesn't need to be flattend.
    if phjGroupVarName is not None:
        phjColIndexNames = pd.Index([phjSuffixDict['joinstr'].join([c[0],c[1]]) for c in phjPropDF.columns.tolist()])
        phjPropDF.columns = phjColIndexNames
    
    phjPropDF = phjPropDF.sort_index(axis = 1)
    
    
    if phjPrintResults == True:
        with pd.option_context('display.float_format','{:,.4f}'.format):
            print(phjPropDF)
    
    

# Plot bar chart of relative frequencies
    if phjPlotProportions == True:
        
        # Plot chart
        phjPlotProportionsBarChart(phjTempDF = phjPropDF,
                                   phjCategoriesToPlotList = phjColumnsList,
                                   phjGroupVarName = phjGroupVarName,
                                   phjGroupLevelsList = phjGroupLevelsList,
                                   phjAlpha = phjAlpha,
                                   phjGraphTitle = None,
                                   phjXAxisTitle = None,
                                   phjYAxisTitle = 'Proportions',
                                   phjPrintResults = True)


    return phjPropDF



# Calculates relative frequencies and multinomial confidence intervals
# --------------------------------------------------------------------
# This function calculates proportions, simultaneous confidence intervals for a categorical
# variable and plots bar charts with asymmetrical error bars.

def phjCalculateMultinomialProportions(phjTempDF,
                                       phjCategoryVarName = None,
                                       phjGroupVarName = None,
                                       phjMissingValue = 'missing',
                                       phjMultinomialConfIntMethod = 'goodman',
                                       phjAlpha = 0.05,
                                       phjPlotRelFreq = True,
                                       phjCategoriesToPlotList = 'all',
                                       phjGroupsToPlotList = 'all',   # Currently not implemented
                                       phjGraphTitle = None,
                                       phjPrintResults = False):
    
    
    # ERROR CHECKING
    # 1. If phjGroupVarName is None then check that ...
    
    
    # Set default suffixes and join strings to create column names
    # to use in output dataframe.
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    
    # Copy required columns to dataframe
    phjTempDF = phjKeepRequiredData(phjTempDF = phjTempDF,
                                    phjColumnsList = [phjCategoryVarName],
                                    phjGroupVarName = phjGroupVarName,
                                    phjMissingValue = phjMissingValue)
    
    
    # Create lists of unique category and group levels
    # (N.B. If no group name is given, a default value 'group' is used.)
    # i. Categories
    phjCategoryLevelsList = phjGetCategoryLevelsList(phjTempDF = phjTempDF,
                                                     phjCategoryVarName = phjCategoryVarName,
                                                     phjPrintResults = phjPrintResults)
        
    # ii. Groups
    phjGroupLevelsList = phjGetGroupLevelsList(phjTempDF = phjTempDF,
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
            phjTempRelFreqDF = pd.DataFrame(phjTempDF[phjCategoryVarName].value_counts(normalize = phjNormalize))
            phjTempRelFreqDF = phjTempRelFreqDF.rename(columns = {phjCategoryVarName: phjSuffix})

            # Use non-normalized data to calculate simultaneous confidence intervals
            if phjNormalize == False:
                phjTempRelFreqDF = phjCalculateMultinomialConfInts(phjTempDF = phjTempRelFreqDF,
                                                                   phjAbsFreqColumnName = phjSuffix,
                                                                   phjSimultConfIntColumnName = phjSuffixDict['cisuffix'],
                                                                   phjMultinomialConfIntMethod = phjMultinomialConfIntMethod,
                                                                   phjAlpha = phjAlpha,
                                                                   phjPrintResults = phjPrintResults)

            # Join temporary data frame to complete dataframe based on index value.
            phjRelFreqDF = phjRelFreqDF.join(phjTempRelFreqDF)
            
            # Cells in summary dataframe with missing values are converted to zero
            # (N.B. In this bit (when phjGroupVarName is None) the following may not be required
            #  but I haven't confirmed that for certain so have included it anyway.)
            phjRelFreqDF = phjRelFreqDF.fillna(0)
            
            
        else:
            for phjGroup in phjGroupLevelsList:
                phjTempRelFreqDF = pd.DataFrame(phjTempDF.loc[phjTempDF[phjGroupVarName] == phjGroup,phjCategoryVarName].value_counts(normalize = phjNormalize))
                phjTempRelFreqDF = phjTempRelFreqDF.rename(columns = {phjCategoryVarName: phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffix])})
                
                # Use non-normalized data to calculate simultaneous confidence intervals
                if phjNormalize == False:
                    phjTempRelFreqDF = phjCalculateMultinomialConfInts(phjTempDF = phjTempRelFreqDF,
                                                                       phjAbsFreqColumnName = phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffix]),
                                                                       phjSimultConfIntColumnName = phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix']]),
                                                                       phjMultinomialConfIntMethod = phjMultinomialConfIntMethod,
                                                                       phjAlpha = phjAlpha,
                                                                       phjPrintResults = phjPrintResults)

    
                # Join temporary data frame to complete dataframe based on index value.
                phjRelFreqDF = phjRelFreqDF.join(phjTempRelFreqDF)
                
            # Cells in summary dataframe with missing values are converted to zero
            phjRelFreqDF = phjRelFreqDF.fillna(0)
    
    
    
    phjRelFreqDF = phjReorderCols(phjTempDF = phjRelFreqDF,
                                  phjGroupVarName = phjGroupVarName,
                                  phjGroupLevelsList = phjGroupLevelsList,
                                  phjAlpha = phjAlpha,
                                  phjPrintResults = False)
    
    if phjPrintResults == True:
        print(phjRelFreqDF)
    
    
    # Plot bar chart of relative frequencies
    if phjPlotRelFreq == True:
        
        # Plot chart
        phjPlotProportionsBarChart(phjTempDF = phjRelFreqDF,
                                   phjCategoriesToPlotList = phjCategoriesToPlotList,
                                   phjGroupVarName = phjGroupVarName,
                                   phjGroupLevelsList = phjGroupLevelsList,
                                   phjAlpha = phjAlpha,
                                   phjGraphTitle = phjGraphTitle,
                                   phjXAxisTitle = phjCategoryVarName,
                                   phjYAxisTitle = 'Relative frequency',
                                   phjPrintResults = False)
    
    
    return phjRelFreqDF



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
                     'numbertrials':'obs',                             # Number of trials (used to calculate binomial proportions)
                     'absfreq':'count',                                # Absolute frequency suffix (used to calcuate multinomial proportions)
                     'proportion':'prop',                              # Relative frequency suffix (used to calcuate multinomial proportions)
                     'totalnumber':'total',                            # Total number (e.g. cases plus controls)
                     'cisuffix':phjCISuffix(phjAlpha,phjCIAbbrev),     # Confidence interval suffix
                     'cilowlim':'llim',                                # lower limit of confidence interval
                     'ciupplim':'ulim',                                # upper limit of confidence interval
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
                      phjMissingValue = 'missing'):
    
    # Get a list of the terms used to head columns in summary tables.
    # (The alpha value is not required and can be left as default.)
    phjSuffixDict = phjDefineSuffixDict()
    
    phjSummaryDF = pd.DataFrame(index = phjColumnsList, columns = [phjSuffixDict['numbertrials'],
                                                                   phjSuffixDict['numbersuccesses']])
    
    for var in phjColumnsList:
        phjSummaryDF.loc[var,phjSuffixDict['numbertrials']] = ((x[var].replace(phjMissingValue,np.nan).dropna()) == 'yes').count()
        phjSummaryDF.loc[var,phjSuffixDict['numbersuccesses']] = ((x[var].replace(phjMissingValue,np.nan).dropna()) == 'yes').sum()
    
    return phjSummaryDF



def phjCalculateBinomialConfInts(phjTempDF,
                                 phjSuccessesColumnName = None,
                                 phjNColumnName = None,
                                 phjBinomialConfIntMethod = 'normal',
                                 phjAlpha = 0.05,
                                 phjPrintResults = False):
    
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Get binomial confidence intervals
    phjBinomConfIntArr = smprop.proportion_confint(count = phjTempDF[phjSuccessesColumnName],
                                                   nobs = phjTempDF[phjNColumnName],
                                                   alpha = phjAlpha,
                                                   method = phjBinomialConfIntMethod)
    
    phjTempDF[phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])] = [i for i in phjBinomConfIntArr[0]]
    phjTempDF[phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])] = [i for i in phjBinomConfIntArr[1]]
    
    return phjTempDF



def phjKeepRequiredData(phjTempDF,
                        phjColumnsList = None,
                        phjGroupVarName = None,
                        phjMissingValue = 'missing'):
    
    # Copy required columns to dataframe
    if phjGroupVarName is not None:
        phjTempDF = phjTempDF.loc[:,[phjGroupVarName] + phjColumnsList].copy()
    else:
        phjTempDF = phjTempDF.loc[:,phjColumnsList].copy()
    
    # Remove rows with missing values
    phjTempDF = phjTempDF.replace(phjMissingValue,np.nan)
    phjTempDF = phjTempDF.dropna(axis = 0, how = 'any')
    
    return phjTempDF



def phjGetCategoryLevelsList(phjTempDF,
                             phjCategoryVarName = None,
                             phjPrintResults = False):
    
    phjCategoryLevelsList = list(phjTempDF[phjCategoryVarName].unique())
    
    if phjPrintResults == True:
        print('\nCategory levels: ',phjCategoryLevelsList)
    
    return phjCategoryLevelsList



def phjGetGroupLevelsList(phjTempDF,
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
        phjGroupLevelsList = list(phjTempDF[phjGroupVarName].unique())
    
    if phjPrintResults == True:
        print('Group levels: ',phjGroupLevelsList,'\n')
    
    return phjGroupLevelsList



def phjCalculateMultinomialConfInts(phjTempDF,
                                    phjAbsFreqColumnName = None,
                                    phjSimultConfIntColumnName = None,
                                    phjMultinomialConfIntMethod = 'goodman',
                                    phjAlpha = 0.05,
                                    phjPrintResults = False):
    
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # Get simultaneous confidence intervals
    phjSimultConfIntArr = smprop.multinomial_proportions_confint(phjTempDF[phjAbsFreqColumnName],
                                                                 alpha = phjAlpha,
                                                                 method = phjMultinomialConfIntMethod)
    
    phjTempDF[phjSuffixDict['joinstr'].join([phjSimultConfIntColumnName,phjSuffixDict['cilowlim']])] = [i[0] for i in phjSimultConfIntArr]
    phjTempDF[phjSuffixDict['joinstr'].join([phjSimultConfIntColumnName,phjSuffixDict['ciupplim']])] = [i[1] for i in phjSimultConfIntArr]
    
    return phjTempDF



def phjReorderCols(phjTempDF,
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
    
    phjTempDF = phjTempDF[phjColOrder]
    
    return phjTempDF



def phjPlotProportionsBarChart(phjTempDF,
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
        phjIndexItemsToPlot = list(phjTempDF.index.values)
    else:
        phjIndexItemsToPlot = phjCategoriesToPlotList
    
    
    if phjGroupVarName is None:                         
        # Calculate y errors
        phjYErrors = phjGetYErrors(phjTempDF = phjTempDF,
                                   phjCategoriesToPlotList = phjIndexItemsToPlot,
                                   phjGroupVarName = phjGroupVarName,
                                   phjGroupLevelsList = phjGroupLevelsList,
                                   phjAlpha = phjAlpha,
                                   phjPrintResults = phjPrintResults)
        
        # Plot bar chart of relative frequencies
        ax = phjTempDF.loc[phjIndexItemsToPlot,
                           phjSuffixDict['proportion']].plot(kind = 'bar',
                                                          title = phjGraphTitle,
                                                          yerr = phjYErrors,
                                                          capsize = 3)
    
    else:
        # Calculate y errors
        phjYErrors = phjGetYErrors(phjTempDF = phjTempDF,
                                   phjCategoriesToPlotList = phjIndexItemsToPlot,
                                   phjGroupVarName = phjGroupVarName,
                                   phjGroupLevelsList = phjGroupLevelsList,
                                   phjAlpha = phjAlpha,
                                   phjPrintResults = phjPrintResults)

    
        # Plot bar chart of relative frequencies
        ax = phjTempDF.loc[phjIndexItemsToPlot,
                           [phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['proportion']]) for phjGroup in phjGroupLevelsList]].plot(kind = 'bar',
                                                                                                                                              title = phjGraphTitle,
                                                                                                                                              yerr = phjYErrors,
                                                                                                                                              capsize = 3)
    
    ax.set_ylabel(phjYAxisTitle)
    ax.set_xlabel(phjXAxisTitle)
    ax.legend(labels = phjGroupLevelsList)
    
    return



def phjGetYErrors(phjTempDF,
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
    # not work e.g. phjTempDF.loc[['A','B'],'col1'].tolist() works, but
    #               phjTempDF.loc[['A','B'],['col1']].tolist() does not.
    #
    # Remember, the CI functions produces the lower and upper limits of the CI whereas the
    # error bars plot the intervals between the proportion and the upper and lower limits.
    # Therefore, it is necessary to calculate the difference between proportion and CI limits
    # in order to plot error bars.
    
    if phjGroupVarName is None:
        phjYErrors = [[ (phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict[phjParameterValue]] - phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])]).tolist(),
                        (phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])] - phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict[phjParameterValue]]).tolist() ]]
    
    else:
        phjYErrors = [[ (phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict[phjParameterValue]])] - phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix'],phjSuffixDict['cilowlim']])]).tolist(),
                        (phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict['cisuffix'],phjSuffixDict['ciupplim']])] - phjTempDF.loc[phjCategoriesToPlotList,phjSuffixDict['joinstr'].join([str(phjGroup),phjSuffixDict[phjParameterValue]])]).tolist() ] for phjGroup in phjGroupLevelsList]
    
    
    #if phjPrintResults == True:
    #    print("\nErrors:")
    #    print(phjYErrors)
        
    return phjYErrors



if __name__ == '__main__':
    main()

