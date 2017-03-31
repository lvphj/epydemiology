# epydemiology
Library of python code for epidemiologists – eventually

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
