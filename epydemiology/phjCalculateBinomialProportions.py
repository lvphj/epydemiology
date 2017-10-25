"""
This function calculates the binomial proportions of a series of binomial variables
for each level of a given group variable. The dataframe has the following format:

        group     A    B    C
    0      g1   yes   no  yes
    1      g1   yes  NaN  yes
    2      g2    no  NaN  yes
    3      g1    no  yes  NaN
    4      g2    no  yes   no
    5      g2    no  yes  yes
    6      g1    no  yes  yes
    7      g1   yes   no  yes
    8      g2   NaN   no   no
    9      g1   yes   no   no

 ...and produces the following dataframe:

    group   var   count   success   propn
       g1     A       6         4    0.66
       g1     B       5         2    0.40
       g1     C       5         4    0.80
       g2     A       3         0    0.00
       g2     B       4         2    0.50
       g2     C       4         2    0.50
    
    
1. NEED TO CHECK that all variables in var list are in the dataframe.
2. NEED TO CHECK that group var is not included in list of columns
3. IF GROUPS TO PLOT IS A LIST AND GROUP VAR NAME IS NONE THEN CHECK
"""


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



def phjCalculateBinomialProportions(phjTempDF,
                                    phjColumnsList = None,
                                    phjSuccess = 'yes',
                                    phjMissingValue = 'missing',
                                    phjGroupVarName = None,
                                    phjConfidenceIntervalType = 'normal',
                                    phjConfidenceIntervalLevel = 0.95,
                                    phjPlotResults = True,
                                    phjGroupsToPlotList = 'all',
                                    phjSortProportions = False,
                                    phjGraphTitle = None,
                                    phjPrintResults = False):
    
    
    if phjGroupVarName is None:
        # If no group var name is supplied then calculate success for
        # whole columns and return summary dataframe.
        phjPropDF = phjCountSuccesses(x = phjTempDF[phjColumnsList],
                                      phjColumnsList = phjColumnsList)
    
    else:
        # Copy required columns to new dataframe
        phjTempDF = phjTempDF[phjColumnsList + [phjGroupVarName]].copy()

        # Calculate number of successes for each level of group variable and return summary dataframe
        phjPropDF = phjTempDF.groupby(phjGroupVarName).apply(lambda x: phjCountSuccesses(x,
                                                                                         phjColumnsList = phjColumnsList))
    
    
    phjPropDF = phjPropDF.reset_index(drop = False)
    
    phjPropDF['proportion'] = phjPropDF['success'] / phjPropDF['count']
    
    if phjSortProportions != False:
        if phjSortProportions == 'asc':
            phjPropDF = phjPropDF.sort_values(by = 'proportion',
                                              axis = 0
                                              ascending = True)
                                              
        elif phjSortProportions == 'desc':
            phjPropDF = phjPropDF.sort_values(by = 'proportion',
                                              axis = 0
                                              ascending = False)
            
        else:
            print('Option for sorting does not exist.')
            
    
    if phjConfidenceIntervalType == 'normal':
        # Calculate standard error
        phjPropDF['stderr'] = ((phjPropDF['proportion'] * (1 - phjPropDF['proportion'])) / phjPropDF['count']).pow(1/2)
        
        # Calculate reliability coefficient
        phjReliabilityCoefficient = norm.ppf(1 - ((1 - phjConfidenceIntervalLevel)/2))
        
        # Calculate confidence interval
        phjCIColumnName = str(int(phjConfidenceIntervalLevel *100)) + 'ci'
        phjPropDF[phjCIColumnName] = phjReliabilityCoefficient * phjPropDF['stderr']
        
        # Calculate uppper and lower CI limits
        phjPropDF['lowCILimit'] = phjPropDF['proportion'] - phjPropDF[phjCIColumnName]
        phjPropDF['uppCILimit'] = phjPropDF['proportion'] + phjPropDF[phjCIColumnName]
        
        
    else:
        phjPropDF['stderr'] = np.nan
        
    
    if phjPrintResults == True:
        with pd.option_context('display.float_format','{:,.4f}'.format):
            print(phjPropDF)
    
    
    if phjPlotResults == True:
        phjPlotProportions(phjTempDF = phjPropDF,
                           phjGroupVarName = phjGroupVarName,
                           phjGroupsToPlotList = 'all',
                           phjCIColumnName = phjCIColumnName,
                           phjGraphTitle = phjGraphTitle)
    
    
    return phjPropDF



def phjCountSuccesses(x,
                      phjColumnsList):
    
    phjSummaryDF = pd.DataFrame(columns = phjColumnsList, index = ['count','success'])
    
    for var in phjColumnsList:
        phjSummaryDF.loc['count',var] = ((x[var].dropna()) == 'yes').count()
        phjSummaryDF.loc['success',var] = ((x[var].dropna()) == 'yes').sum()
    
    # Transpose
    phjSummaryDF = phjSummaryDF.T
    
    # Rename index
    phjSummaryDF.index.name = 'var'
    
    return phjSummaryDF



def phjPlotProportions(phjTempDF,
                       phjGroupVarName = None,
                       phjGroupsToPlotList = None,
                       phjCIColumnName = None,
                       phjGraphTitle = None):
    
    # Plot graphs
    # ===========
    # If no group var name is provided then assume plot all rows
    if phjGroupVarName is None:
        if phjGraphTitle is None:
            phjTempDF.plot(x = 'var',
                           y = 'proportion',
                           kind = 'bar',
                           title = 'Proportions',
                           legend = False,
                           yerr = phjCIColumnName)
        else:
            phjTempDF.plot(x = 'var',
                           y = 'proportion',
                           kind = 'bar',
                           title = phjGraphTitle,
                           legend = False,
                           yerr = phjCIColumnName)
    
    else:
        if phjGroupsToPlotList == 'all':
            phjGroupsToPlotList = phjTempDF[phjGroupVarName].unique()
        
        for i, phjGroup in phjTempDF.groupby(phjGroupVarName):
            if i in phjGroupsToPlotList:
                if phjGraphTitle is None:
                    phjTempDF.loc[phjTempDF[phjGroupVarName] == i,:].plot(x = 'var',
                                                                          y = 'proportion',
                                                                          kind = 'bar',
                                                                          title = 'Group ' + i,
                                                                          legend = False,
                                                                          yerr = phjCIColumnName)
                else:
                    phjTempDF.loc[phjTempDF[phjGroupVarName] == i,:].plot(x = 'var',
                                                                          y = 'proportion',
                                                                          kind = 'bar',
                                                                          title = phjGraphTitle,
                                                                          legend = False,
                                                                          yerr = phjCIColumnName)

            plt.show()

    return
    
    
if __name__ == '__main__':
main()
