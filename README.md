# epydemiology
Library of python code for epidemiologists – eventually

## phjOddsRatio()
### Function description
#### Introduction
This function can be used to calculate odds ratios and 95% confidence intervals for case-control studies. The function is pass a Pandas dataframe containing the data together with the name of the 'case' variable and potential risk factor variable. The function returns a Pandas dataframe based on a 2 x 2 or n x 2 contingency table together with columns containing the odds, odds ratio and 95% confidence intervals (Woolf).

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
