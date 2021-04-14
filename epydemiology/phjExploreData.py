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
    import statsmodels.formula.api as smf
    import statsmodels.api as sm


import re
import collections
import inspect



# Import minor epydemiology functions from other epydemiology files
# -----------------------------------------------------------------
# In order to use the phjDefineSuffixDict() function from a different .py file in the
# same package, it seems that we need to import that function explicitly. This can be
# done using the same format as in the __init__.py file e.g.:
#     from .pythonFileName import functionName
# Where the pythonFileName is a file in the same package.
# For more details, see tutorial at https://www.youtube.com/watch?v=0oTh1CXRaQ0.

from .phjRROR import phjOddsRatio
from .phjRROR import phjRemoveNaNRows
from .phjCalculateProportions import phjDefineSuffixDict
from .phjCalculateProportions import phjGetYErrors
from .phjExtFuncs import getJenksBreaks
from .phjTestFunctionParameters import phjAssert



# ==============
# Main functions
# ==============
#
def phjViewLogOdds(phjDF,
                   phjBinaryDepVarName = None,   # This is a required variable therefore setting default to None
                                                 # is not required but all parameters without default values need
                                                 # to be defined first which would change the order in which
                                                 # parameters are defined; and order is useful to ensure correct
                                                 # values are defined.
                   phjCaseValue = 1,
                   phjContIndepVarName = None,
                   phjMissingValue = np.nan,
                   phjNumberOfCategoriesInt = 5,
                   phjNewCategoryVarName = None,
                   phjCategorisationMethod = 'jenks',   # Need to be able to pass a list of cut-off values here as well.
                   phjGroupVarName = None,
                   phjAlpha = 0.05,
                   phjPrintResults = False):
    
    # In several functions, it's useful to have access to a dict containing column headings
    # and suffixes used in a variety of situations.
    phjSuffixDict = phjDefineSuffixDict()
    
    # Create a name for the new categorical variable by replacing all spaces with underscores
    # and adding the suffix to indicate that a continuous variable has been converted to a category.
    if phjNewCategoryVarName is None:
        phjNewCategoryVarName = phjSuffixDict['joinstr'].join([phjContIndepVarName.replace(' ','_'),
                                                               phjSuffixDict['categorisedvar']])
    
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjBinaryDepVarName',phjBinaryDepVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        phjAssert('phjCaseValue',phjCaseValue,(str,int,float),phjAllowedOptions = list(phjDF[phjBinaryDepVarName].replace(phjMissingValue,np.nan).dropna().unique()))
        phjAssert('phjContIndepVarName',phjContIndepVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        phjAssert('phjMissingValue',phjMissingValue,(str,int,float))
        phjAssert('phjNumberOfCategoriesInt',phjNumberOfCategoriesInt,int,phjAllowedOptions = {'min':2,'max':len(phjDF.index)})
        phjAssert('phjNewCategoryVarName',phjNewCategoryVarName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjCategorisationMethod',phjCategorisationMethod,(str,collections.abc.Mapping))
        
        if phjGroupVarName is not None:
            phjAssert('phjGroupVarName',phjGroupVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        
        phjAssert('phjAlpha',phjAlpha,float,phjAllowedOptions = {'min':0.0001,'max':0.9999})
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
    except AssertionError as e:
        
        # Assign value to variable phjOR which will be returned at end of function.
        phjOR = None
        
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
        # Retain only those columns that will be analysed (otherwise, it is feasible that
        # unrelated columns that contain np.nan values will cause removal of rows in
        # unexpected ways.
        phjDF = phjDF[[col for col in [phjBinaryDepVarName,phjContIndepVarName,phjGroupVarName] if col is not None]]
        
        # Data to use - remove rows that have a missing value
        phjDF = phjRemoveNaNRows(phjDF = phjDF,
                                 phjCaseVarName = phjBinaryDepVarName,
                                 phjRiskFactorVarName = phjContIndepVarName,
                                 phjMissingValue = phjMissingValue)
        
        # Deep copy phjDF to phjDF to avoid errors relating editing dataframe slice
        phjDF = phjDF.copy(deep = True)
        
        # Convert a continuous variable to a categorical variable using a variety of methods.
        # If phjReturnBreaks = True then function also returns a list of the break points
        # for the continuous variable.
        phjDF, phjBreaks = phjCategoriseContinuousVariable(phjDF = phjDF,
                                                           phjContinuousVarName = phjContIndepVarName,
                                                           phjMissingValue = phjMissingValue,
                                                           phjNumberOfCategoriesInt = phjNumberOfCategoriesInt,
                                                           phjNewCategoryVarName = phjNewCategoryVarName,
                                                           phjCategorisationMethod = phjCategorisationMethod,
                                                           phjReturnBreaks = True,
                                                           phjPrintResults = phjPrintResults)
        
        
        print('Third DF')
        print(phjBreaks)
        print(phjDF)
        
        
        
        # If the breaks have been calculated (and the continuous variable categorised successfully)
        # then plot the graph of logodds against mid-points
        if phjBreaks is not None:
        
            # The following DF contains an index that may be numeric.
            phjOR = phjOddsRatio(phjDF = phjDF,
                                 phjCaseVarName = phjBinaryDepVarName,
                                 phjCaseValue = phjCaseValue,
                                 phjRiskFactorVarName = phjNewCategoryVarName,
                                 phjRiskFactorBaseValue = 0,   # Use the minimum value as the base value (but it's not important in this context)
                                 phjMissingValue = phjMissingValue,
                                 phjAlpha = phjAlpha,
                                 phjPrintResults = phjPrintResults)
            
            
            print('Fourth DF')
            print(phjOR)
            
            
            if phjOR is not None:
                
                phjOR[phjSuffixDict['logodds']] = np.log(phjOR[phjSuffixDict['odds']])
                
                # Calculate log odds using logistic regression and retrieve the se from the statistical model
                phjSE = phjCalculateLogOddsSE(phjDF = phjDF,
                                              phjCaseVarName = phjBinaryDepVarName,
                                              phjCaseValue = phjCaseValue,
                                              phjCategoricalVarName = phjNewCategoryVarName,
                                              phjMissingValue = phjMissingValue,
                                              phjAlpha = phjAlpha,
                                              phjPrintResults = phjPrintResults)
                
                # Join to phjOR dataframe
                phjOR = phjOR.join(phjSE)
                
                
                # Calculate lower and upper limits assuming normal distribution
                phjRelCoef = norm.ppf(1 - (phjAlpha/2))
                
                phjOR[phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],
                                                     phjSuffixDict['cilowlim']])] = phjOR[phjSuffixDict['logodds']] - (phjRelCoef * phjOR[phjSuffixDict['stderr']])
                
                phjOR[phjSuffixDict['joinstr'].join([phjSuffixDict['cisuffix'],
                                                     phjSuffixDict['ciupplim']])] = phjOR[phjSuffixDict['logodds']] + (phjRelCoef * phjOR[phjSuffixDict['stderr']])
                
                
                # Calculae midpoints of categories
                phjOR[phjSuffixDict['catmidpoints']] = [((phjBreaks[i] + phjBreaks[i+1]) / 2) for i in range(len(phjBreaks) - 1)]
                
                
                # Plot log odds against midpoints of categories
                phjYErrors = phjGetYErrors(phjDF = phjOR,
                                           phjCategoriesToPlotList = phjOR.index.tolist(),
                                           phjParameterValue = 'logodds',
                                           phjGroupVarName = None,
                                           phjGroupLevelsList = None,
                                           phjAlpha = phjAlpha,
                                           phjPrintResults = phjPrintResults)
                
                ax = phjOR.plot(x = phjSuffixDict['catmidpoints'],
                                y = phjSuffixDict['logodds'],
                                kind = 'line',
                                yerr = phjYErrors,
                                capsize = 4,
                                title = 'Log-odds against mid-points of categories')
                ax.set_ylabel("Log odds")
                ax.set_xlabel(phjNewCategoryVarName)
                ax.set_xlim([phjBreaks[0],phjBreaks[-1]])
                
                # Add vertical lines to indicate boundaries of categories
                for xline in phjBreaks:
                    ax.axvline(x = xline,
                               linestyle = 'dashed',
                               color = 'gray')
        
        else:
            # Otherwise, attempts to categorise the data failed and phjBreaks returned as None
            phjOR = None
    
    if phjPrintResults == True:
        print('\nOdds ratio dataframe')
        print(phjOR)
    
    return phjOR




# ====================
# Supporting functions
# ====================

def phjCalculateLogOddsSE(phjDF,
                          phjCaseVarName,
                          phjCaseValue,
                          phjCategoricalVarName,
                          phjMissingValue = np.nan,
                          phjAlpha = 0.05,
                          phjPrintResults = False):
    
    
    # Get a list of the terms used to head columns in summary tables
    phjSuffixDict = phjDefineSuffixDict(phjAlpha = phjAlpha)
    
    # statsmodels has some slightly unexpected behaviour if outcome variable contains
    # strings (see https://stackoverflow.com/questions/48312979/how-does-statsmodels-encode-endog-variables-entered-as-strings).
    # Convert to case variable to 0/1 for logistic regression model.
    # The original calculation of odds table in phjOddsRatio() function checks to make
    # sure there are only 2 levels present in the case variable and that the case value
    # is actually present in the column so no need to check again.
    # Get a list of values in the case variable, create a dictionary to convert values
    # to binary representation (based on given value of case value) – assuming it's not
    # already binary – and use the dictionary to convert case variable to a binary format.
    phjCaseLevelsList = phjDF[phjCaseVarName].unique()
    
    if set(phjCaseLevelsList) != set([0,1]):
        phjBinaryConvertDict = {c:(1 if c==phjCaseValue else 0) for c in phjCaseLevelsList}
        phjDF[phjCaseVarName] = phjDF[phjCaseVarName].replace(phjBinaryConvertDict)
    
    # Run a logistic regression model with no constant term (in patsy package, the -1 removes the constant term)
    phjLogisticRegressionResults = smf.glm(formula='{0} ~ C({1}) -1'.format(phjCaseVarName,phjCategoricalVarName),
                                           data=phjDF,
                                           family = sm.families.Binomial(link = sm.genmod.families.links.logit)).fit()
    
    if phjPrintResults == True:
        print('\nResults of logistic regression model')
        print(phjLogisticRegressionResults.summary())
    
    # Extract group codes from index of logistic regression results table.
    # The index values have the structure: varName[level].
    # Extract just the bit contained in square brackets:
    
    # i. Define and compile regex
    #    (Picks out integer or floats from within square brackets)
    phjRegex = re.compile('\[(?P<group_index>\d+.?\d*)\]$')
    
    # ii. Extract std err data from model
    phjSEResultsDF = pd.DataFrame(phjLogisticRegressionResults.bse)
    
    # iii. Rename column heading and generate a new index and replace the old one.
    phjSEResultsDF.columns = [phjSuffixDict['stderr']]
    
    # The following list comprehension steps through each index and extracts the regex
    # group (in this case, the bit between the square brackets)
    phjNewIndex = [re.search(phjRegex,i).group('group_index') for i in phjSEResultsDF.index]
    
    # ...and the extracted bits are converted to ints if possible
    for n,j in enumerate(phjNewIndex):
        try:
            phjNewIndex[n] = int(float(j))   # Can't convert a string of a float to int using int(); need to use float() as well.
        except ValueError:
            phjNewIndex[n] = j
            
    phjSEResultsDF.index = phjNewIndex
    
    
    return phjSEResultsDF




def phjCategoriseContinuousVariable(phjDF,
                                    phjContinuousVarName = None,
                                    phjMissingValue = np.nan,
                                    phjNumberOfCategoriesInt = 5,
                                    phjNewCategoryVarName = None,
                                    phjCategorisationMethod = 'jenks',
                                    phjReturnBreaks = False,
                                    phjPrintResults = False):
    
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjContinuousVarName',phjContinuousVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        phjAssert('phjMissingValue',phjMissingValue,(str,int,float))
        phjAssert('phjNumberOfCategoriesInt',phjNumberOfCategoriesInt,int,phjAllowedOptions = {'min':2,'max':min([100,len(pd.to_numeric(phjDF[phjContinuousVarName],errors = 'coerce').dropna(axis = 0))])})
        phjAssert('phjNewCategoryVarName',phjNewCategoryVarName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        
        # Check phjCategorisationMethod is either a string indicating method to use to
        # calculate breaks or a list giving required breaks.
        # If a string is entered, check it is one of the recognised options.
        # If a list is entered, check it contains only numbers and that each consecutive
        # number is greater than the number preceding it.
        phjAssert('phjCategorisationMethod',phjCategorisationMethod,(str,list))
        if isinstance(phjCategorisationMethod,str):
            phjAssert('phjCategorisationMethod', phjCategorisationMethod.lower(), str,
                      phjBespokeMessage = "The selected method to calculate category boundaries is not recognised or has not yet been implemented. The variable '{}' has not been categorised.".format(phjContinuousVarName),
                      phjAllowedOptions = ['quantile','jenks'])
        elif isinstance(phjCategorisationMethod,collections.Sequence):
            assert phjCheckListOfIncreasingNumbers(phjList = phjCategorisationMethod) == True, "The list entered for phjCategorisationMethod must contain sequentially increasing numbers."
        
        phjAssert('phjReturnBreaks',phjReturnBreaks,bool)
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
    except AssertionError as e:
        
        # Define phjBreaks before returning at end of function
        if phjReturnBreaks == True:
            phjBreaks = None
        
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
        # Check if phjCategorisationMethod is a list.
        # If so, the phjNumberOfCategoriesInt is ignored and the number of categories
        # is inferred from the break points.
        if isinstance(phjCategorisationMethod,collections.Sequence) and not isinstance(phjCategorisationMethod,str):
            
            phjBreaks = phjCategorisationMethod
            
            phjDF[phjNewCategoryVarName] = pd.cut(phjDF[phjContinuousVarName],
                                                  bins = phjBreaks,
                                                  right = True,
                                                  labels = False)
        
        elif isinstance(phjCategorisationMethod,str):
            if phjCategorisationMethod.lower() == 'jenks':
            
                phjBreaks = phjImplementGetBreaks(phjDF = phjDF,
                                                  phjContinuousVarName = phjContinuousVarName,
                                                  phjMissingValue = phjMissingValue,
                                                  phjNumberOfCategoriesInt = phjNumberOfCategoriesInt,
                                                  phjPrintResults = phjPrintResults)
                
                # Cut data series based on Jenks breaks
                phjDF[phjNewCategoryVarName] = pd.cut(phjDF[phjContinuousVarName],
                                                          bins = phjBreaks,
                                                          right = True,
                                                          labels = False)
                
                if phjPrintResults == True:
                    print('Category quantile bins (Jenks) = ',phjBreaks)
                    print('\n')
            
            
            elif phjCategorisationMethod.lower() == 'quantile':
            
                # Cut data series based on quantiles / number of required bins
                phjDF[phjNewCategoryVarName], phjBreaks = pd.cut(phjDF[phjContinuousVarName],
                                                                     bins = phjNumberOfCategoriesInt,
                                                                     right = True,
                                                                     retbins = True,
                                                                     labels = False)
                
                if phjPrintResults == True:
                    print('Category quantile bins (quantile) = ',phjBreaks)
                    print('\n')
    
    
    if phjReturnBreaks == True:
        return phjDF,phjBreaks
    else:
        return phjDF




def phjCheckListOfIncreasingNumbers(phjList):
    # This function checks that the list contains only numbers and that
    # the numbers are consecutively increasing.
    if isinstance(phjList,collections.Sequence) and not isinstance(phjList,str):
        # List comprehension steps through each value of list
        # and only retains the numbers. If the length of the orginal
        # list is different from the list with numbers only, then
        # some items were not numbers
        if len(phjList) == len([i for i in phjList if phjCheckIsNumber(i) == True]):
            # If all items are numbers, check that each consecutive number
            # is bigger than the preceding one
            phjIncrease = True
            for j in range(1,len(phjList)):
                if (phjIncrease == True) and (phjList[j] - phjList[j-1] > 0):
                    phjIncrease = True
                else:
                    phjIncrease = False
                    print('Item at position {0} in list ({1}) is not larger than preceding number ({2}).'.format(j,phjList[j],phjList[j-1]))
                    break

            if phjIncrease == True:
                phjListCheck = True
            else:
                phjListCheck = False

        else:
            # Here, could identify which list items are not numbers if so inclined...
            print('Some items in list are not numbers.')
            phjListCheck = False
    
    return phjListCheck




def phjCheckIsNumber(i):
    try:
        i = float(i)
        phjIsNumber = True
    except ValueError:
        phjIsNumber = False
    except TypeError:
        phjIsNumber = False
    return phjIsNumber




def phjImplementGetBreaks(phjDF,
                          phjContinuousVarName = None,
                          phjMissingValue = 'missing',
                          phjNumberOfCategoriesInt = 5,
                          phjCategorisationMethod = 'jenks',
                          phjPrintResults = False):
    
    phjTempSer = phjDF[phjContinuousVarName].replace('missing',np.nan).dropna(axis = 0)
    
    if phjCategorisationMethod == 'jenks':
        if len(phjTempSer.index) <= 1000:
            phjBreaks = getJenksBreaks(np.array(phjTempSer),
                                       phjNumberOfCategoriesInt)
        
        else:
            phjBreaks = getJenksBreaks(np.array(phjTempSer.sample(1000)),
                                       phjNumberOfCategoriesInt)
            # As the breaks were calculated from a sample, the last value
            # may be smaller than the maximum. Hence, when categorising the
            # continuous variable in the original dataframe, there would be a
            # small number of individuals who wouldn't appear in any category.
            # Replace the end values of the break list with values that are
            # slightly bigger or smaller (0.1%) than the maximum or minimum.
            # This is the same procedure used by pandas.cut() method.
            phjBreaks[0] = phjTempSer.min() * 0.999
            phjBreaks[-1] = phjTempSer.max() * 1.001
    
    else:
        print('The selected method to calculate category boundaries has not yet been implemented.')
        phjBreaks = None
    
    return phjBreaks




if __name__ == '__main__':
    main()
