# epydemiology
Library of python code for epidemiologists – eventually

## Installation
'''python
pip install epydemiology
'''

Functions can then be accessed using:

'''myDF = phjSelectCaseControlDataset()''' – select matched or unmatched case-control data.

myDF = phjOddsRatio() – calculate odds and odds ratio for case-control studies.

myDF = phjRelativeRisk() – calculate relative risks for cross-sectional or longitudinal studies.


## phjSelectCaseControlDataset()
Python function to randomly select matched or unmatched case-control data.
### Function description
#### Introduction
This function selects case-control datasets from the SAVSNET database. It receives, as parameters, two Pandas dataframes, one containing known cases and, the other, potential controls. The algorithm steps through each case in turn and selects the relevant number of control subjects from the second dataframe, matching on the list of variables. The function then adds the details of the case and the selected controls to a separate, pre-defined dataframe before moving onto the next case.

Initially, the phjSelectCaseControlDataset() function calls phjParameterCheck() to check that passed parameters meet specified criteria (e.g. ensure lists are lists and ints are ints etc.). If all requirements are met, phjParameterCheck() returns True and phjSelectCaseControlDataset() continues.

The function requires a parameter called phjMatchingVariablesList. If this parameter is None (the default), an unmatched case-control dataset is produced. If, however, the parameter is a list of variable names, the function will return a dataset where controls have been matched on the variables in the list.

The phjSelectCaseControlDataset() function proceeds as follows:

1. Creates an empty dataframe in which selected cases and controls will be stored.
2. Steps through each case in the phjCasesDF dataframe, one at a time.
3. Gets data from matched variables for the case and store in a dict
4. Creates a mask for the controls dataframe to select all controls that match the cases in the matched variables
5. Applies mask to controls dataframe and count number of potential matches
6. Adds cases and controls to dataframe (through call to phjAddRecords() function)
7. Removes added control records from potential controls database so single case cannot be selected more than once
8. Returns Pandas dataframe containing list of cases and controls. This dataframe only contains columns for unique identifier, case and group id. It will, therefore need to be merged with the full database to get and additional required columns.

### Description of function parameters
1. **phjCasesDF** Pandas dataframe containing list of cases.
2. **phjPotentialControlsDF** Pandas dataframe containing a list of potential control cases.
3. **phjUniqueIdentifierVarName** Name of variable that acts as a unique identifier (e.g. consulations ID number would be a good example). N.B. In some cases, the consultation number is not unique but has been entered several times in the database, sometimes in very quick succession (ms). Data must be cleaned to ensure that the unique identifier variable is, indeed, unique.
4. **phjMatchingVariablesList** (Default = None.) List of variable names for which the cases and controls should be matched. Must be a list. The default is None. If 
5. **phjControlsPerCaseInt** (Default = 1.) Number of controls that should be selected per case.
6. **phjPrintResults** (Default= False.) Print verbose output during execution of scripts. If running on Jupyter-Notebook, setting PrintResults = True causes a lot a output and can cause problems connecting to kernel.

### Exceptions raised
None

### Returns
Pandas dataframe containing a column containing the unique identifier variable, a column containing case/control identifier and – for matched case-control studies – a column containing a group identifier. The returned dataframe will need to be left-joined with another dataframe that contains additional required variables.

### Other notes
Setting phjPrintResults = True can cause problems when running script on Jupyiter-Notebook.


## phjOddsRatio()
### Function description
#### Introduction
This function can be used to calculate odds ratios and 95% confidence intervals for case-control studies. The function is passed a Pandas dataframe containing the data together with the name of the 'case' variable and the name of the potential risk factor variable. The function returns a Pandas dataframe based on a 2 x 2 or n x 2 contingency table together with columns containing the odds, odds ratios and 95% confidence intervals (Woolf). Rows that contain a missing value in either the case variable or the risk factor variable are removed before calculations are made.

### Description of function parameters
The function takes the following parameters:

```python
phjOddsRatio(phjTempDF,
             phjCaseVarName,
             phjCaseValue,
             phjRiskFactorVarName,
             phjRiskFactorBaseValue)
```

1. **phjTempDF**
  * This is a Pandas dataframe that contains the data to be analysed. One of the variables should be contain a variable indicating whether the row is a case or a control.

2. **phjCaseVarName**
  * Name of the variable that indicates whether the row is a case or a control.

3. **phjCaseValue**
  * The value used in phjCaseVarName variable to indicate a case (e.g. True, yes, 1, etc.)

4. **phjRiskFactorVarName**
  * The name of the potential risk factor to be analysed. This needs to be a categorical variable.

5. **phjRiskFactorBaseValue**
  * The level or stratum of the potential risk factor that will be used as the base level in the calculation of odds ratios.

### Exceptions raised
None

### Returns
Pandas dataframe containing a cross-tabulation of the case and risk factor varible. In addition, odds, odds ratios and 95% confidence interval (Woolf) of the odds ratio is presented.

### Other notes
None

### Example
An example of the function in use is given below:

```python
tempDF = pd.DataFrame({'caseN':[1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
                       'caseA':['y','y','y','y','y','y','y','y','n','n','n','n','n','n','n','n','n','n','n','n'],
                       'catN':[1,2,3,2,3,4,3,2,3,4,3,2,1,2,1,2,3,2,3,4],
                       'catA':['a','a','b','b','c','d','a','c','c','d','a','b','c','a','d','a','b','c','a','d'],
                       'floatN':[1.2,4.3,2.3,4.3,5.3,4.3,2.4,6.5,4.5,7.6,5.6,5.6,4.8,5.2,7.4,5.4,6.5,5.7,6.8,4.5]})

phjORTable = phjOddsRatio( phjTempDF = tempDF,
                           phjCaseVarName = 'caseA',
                           phjCaseValue = 'y',
                           phjRiskFactorVarName = 'catA',
                           phjRiskFactorBaseValue = 'a')

pd.options.display.float_format = '{:,.3f}'.format

print(phjORTable)
```

## phjRelativeRisk()
### Function description
#### Introduction
### Description of function parameters
The function takes the following parameters:

```python
phjRelativeRisk(phjTempDF,
                phjCaseVarName,
                phjCaseValue,
                phjRiskFactorVarName,
                phjRiskFactorBaseValue)
```

1. **phjTempDF**
  * This is a Pandas dataframe that contains the data to be analysed. One of the variables should be contain a variable indicating whether the row has disease (diseased) or not (healthy).

2. **phjCaseVarName**
  * Name of the variable that indicates whether the row has disease or is healthy.

3. **phjCaseValue**
  * The value used in phjCaseVarName variable to indicate disease (e.g. True, yes, 1, etc.)

4. **phjRiskFactorVarName**
  * The name of the potential risk factor to be analysed. This needs to be a categorical variable.

5. **phjRiskFactorBaseValue**
  * The level or stratum of the potential risk factor that will be used as the base level in the calculation of odds ratios.

### Exceptions raised
None

### Returns
Pandas dataframe containing a cross-tabulation of the disease status and risk factor varible. In addition, risk, relative risk and 95% confidence interval of the relative risk is presented.

### Other notes
None

### Example
An example of the function in use is given below:

```python
tempDF = pd.DataFrame({'caseN':[1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
                       'caseA':['y','y','y','y','y','y','y','y','n','n','n','n','n','n','n','n','n','n','n','n'],
                       'catN':[1,2,3,2,3,4,3,2,3,4,3,2,1,2,1,2,3,2,3,4],
                       'catA':['a','a','b','b','c','d','a','c','c','d','a','b','c','a','d','a','b','c','a','d'],
                       'floatN':[1.2,4.3,2.3,4.3,5.3,4.3,2.4,6.5,4.5,7.6,5.6,5.6,4.8,5.2,7.4,5.4,6.5,5.7,6.8,4.5]})

phjRRTable = phjRelativeRisk( phjTempDF = tempDF,
                              phjCaseVarName = 'caseA',
                              phjCaseValue = 'y',
                              phjRiskFactorVarName = 'catA',
                              phjRiskFactorBaseValue = 'a')

pd.options.display.float_format = '{:,.3f}'.format

print(phjRRTable)
```
