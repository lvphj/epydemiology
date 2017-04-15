# epydemiology
Library of python code for epidemiologists – eventually.

## A. Installation
```python
pip install epydemiology as epy
```
## B. Usage

The following functions are available:
1. To load data from a named Excel cell range

```python
myDF = epy.phjReadDataFromExcelNamedCellRange()
```

2. To load data from MySQL or SQL SERVER database into Pandas dataframe

```python
myDF = epy.phjGetDataFromDatabase()
```

3. To select matched or unmatced case-control data (without replacement):

```python
myDF = epy.phjSelectCaseControlDataset()
```
4. To calculate odds and odds ratios for case-control studies

```python
myDF = epy.phjOddsRatio()
```
5. To calculate relative risks for cross-sectional or longitudinal studies

```python
myDF = epy.phjRelativeRisk()
```

## C. Details of functions
### 1. phjReadDataFromExcelNamedCellRange()

```python
df = phjReadDataFromExcelNamedCellRange(phjExcelPathAndFileName = None,
                                        phjExcelCellRangeName = None,
                                        phjDatetimeFormat = "%Y-%m-%d %H:%M:%S",
                                        phjMissingValue = "missing",
                                        phjHeaderRow = False,
                                        phjPrintResults = False)
```

Python function to read data from a named cell range in an Excel workbook.

#### Description


#### Function parameters



#### Exceptions raised
None

#### Returns
Pandas dataframe containing data read from named cell range.

#### Other notes
None.

#### Example
An example of the function in use is given below:

```python
Under construction.
```


### 2. phjGetDataFromDatabase()

```python
df = epy.phjGetDataFromDatabase(phjQueryPathAndFileName = None,
                                phjPrintResults = False)
```

Python function to read data from a MySQL or SQL SERVER database.

#### Description


#### Function parameters



#### Exceptions raised
None

#### Returns
Pandas dataframe containing data read from database.

#### Other notes
None.

#### Example
An example of the function in use is given below:

```python
Under construction.
```




### 3. phjSelectCaseControlDataset()

```python
df = epy.phjSelectCaseControlDataset(phjCasesDF,
                                     phjPotentialControlsDF,
                                     phjUniqueIdentifierVarName,
                                     phjMatchingVariablesList = None,
                                     phjControlsPerCaseInt = 1,
                                     phjPrintResults = False)
```

Python function to randomly select matched or unmatched case-control data.
#### Description
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

#### Function parameters
The function takes the following parameters:

1. **phjCasesDF**
  * Pandas dataframe containing list of cases.
2. **phjPotentialControlsDF**
  * Pandas dataframe containing a list of potential control cases.
3. **phjUniqueIdentifierVarName**
  * Name of variable that acts as a unique identifier (e.g. consulations ID number would be a good example). N.B. In some cases, the consultation number is not unique but has been entered several times in the database, sometimes in very quick succession (ms). Data must be cleaned to ensure that the unique identifier variable is, indeed, unique.
4. **phjMatchingVariablesList** (Default = None.)
  * List of variable names for which the cases and controls should be matched. Must be a list. The default is None. If 
5. **phjControlsPerCaseInt** (Default = 1.)
  * Number of controls that should be selected per case.
6. **phjPrintResults** (Default= False.)
  * Print verbose output during execution of scripts. If running on Jupyter-Notebook, setting PrintResults = True causes a lot a output and can cause problems connecting to kernel.

#### Exceptions raised
None

#### Returns
Pandas dataframe containing a column containing the unique identifier variable, a column containing case/control identifier and – for matched case-control studies – a column containing a group identifier. The returned dataframe will need to be left-joined with another dataframe that contains additional required variables.

#### Other notes
Setting phjPrintResults = True can cause problems when running script on Jupyiter-Notebook.

#### Example
An example of the function in use is given below:

```python
import pandas as pd
import epydemiology as epy

casesDF = pd.DataFrame({'animalID':[1,2,3,4,5],'var1':[43,45,34,45,56],'sp':['dog','dog','dog','dog','dog']})
potControlsDF = pd.DataFrame({'animalID':[11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30],
                              'var1':[34,54,34,23,34,45,56,67,56,67,78,98,65,54,34,76,87,56,45,34],
                              'sp':['dog','cat','dog','dog','cat','dog','cat','dog','cat','dog',
                                    'dog','dog','dog','cat','dog','cat','dog','dog','dog','cat']})

print("This dataframe contains all the cases of disease\n")
print(casesDF)
print("\n")
print("This dataframe contains all the animals you could potentially use as controls\n")
print(potControlsDF)
print("\n")

# Selecting unmatched controls
unmatchedDF = epy.phjSelectCaseControlDataset(phjCasesDF = casesDF,
                                              phjPotentialControlsDF = potControlsDF,
                                              phjUniqueIdentifierVarName = 'animalID',
                                              phjMatchingVariablesList = None,
                                              phjControlsPerCaseInt = 2,
                                              phjPrintResults = False)

print(unmatchedDF)
print("\n")

# Selecting controls that are matched to cases on variable 'sp'
matchedDF = epy.phjSelectCaseControlDataset(phjCasesDF = casesDF,
                                            phjPotentialControlsDF = potControlsDF,
                                            phjUniqueIdentifierVarName = 'animalID',
                                            phjMatchingVariablesList = ['sp'],
                                            phjControlsPerCaseInt = 2,
                                            phjPrintResults = False)

print(matchedDF)

```

Output

```
This dataframe contains all the cases of disease

   animalID   sp  var1
0         1  dog    43
1         2  dog    45
2         3  dog    34
3         4  dog    45
4         5  dog    56


This dataframe contains all the animals you could potentially use as controls

    animalID   sp  var1
0         11  dog    34
1         12  cat    54
2         13  dog    34
3         14  dog    23
4         15  cat    34
5         16  dog    45
6         17  cat    56
7         18  dog    67
8         19  cat    56
9         20  dog    67
10        21  dog    78
11        22  dog    98
12        23  dog    65
13        24  cat    54
14        25  dog    34
15        26  cat    76
16        27  dog    87
17        28  dog    56
18        29  dog    45
19        30  cat    34


UNMATCHED CONTROLS

    case  animalID
0      1         1
1      1         2
2      1         3
3      1         4
4      1         5
5      0        22
6      0        13
7      0        30
8      0        18
9      0        25
10     0        28
11     0        14
12     0        15
13     0        24
14     0        19


MATCHED CONTROLS

   animalID group case   sp
0         1     0    1  dog
1        28     0    0  dog
2        16     0    0  dog
3         2     1    1  dog
4        25     1    0  dog
5        27     1    0  dog
6         3     2    1  dog
7        21     2    0  dog
8        11     2    0  dog
9         4     3    1  dog
10       18     3    0  dog
11       14     3    0  dog
12        5     4    1  dog
13       22     4    0  dog
14       29     4    0  dog
```

---

### 4. phjOddsRatio()

```python
df = phjOddsRatio(phjTempDF,
                  phjCaseVarName,
                  phjCaseValue,
                  phjRiskFactorVarName,
                  phjRiskFactorBaseValue)
```

#### Description
This function can be used to calculate odds ratios and 95% confidence intervals for case-control studies. The function is passed a Pandas dataframe containing the data together with the name of the 'case' variable and the name of the potential risk factor variable. The function returns a Pandas dataframe based on a 2 x 2 or n x 2 contingency table together with columns containing the odds, odds ratios and 95% confidence intervals (Woolf). Rows that contain a missing value in either the case variable or the risk factor variable are removed before calculations are made.

#### Function parameters
The function takes the following parameters:

1. **phjTempDF**
  * This is a Pandas dataframe that contains the data to be analysed. One of the columns should be a variable that indicates whether the row is a case or a control.

2. **phjCaseVarName**
  * Name of the variable that indicates whether the row is a case or a control.

3. **phjCaseValue**
  * The value used in phjCaseVarName variable to indicate a case (e.g. True, yes, 1, etc.)

4. **phjRiskFactorVarName**
  * The name of the potential risk factor to be analysed. This needs to be a categorical variable.

5. **phjRiskFactorBaseValue**
  * The level or stratum of the potential risk factor that will be used as the base level in the calculation of odds ratios.

#### Exceptions raised
None

#### Returns
Pandas dataframe containing a cross-tabulation of the case and risk factor varible. In addition, odds, odds ratios and 95% confidence interval (Woolf) of the odds ratio is presented.

#### Other notes
None

#### Example
An example of the function in use is given below:

```python
import pandas as pd
import epydemiology as epy

tempDF = pd.DataFrame({'caseN':[1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
                       'caseA':['y','y','y','y','y','y','y','y','n','n','n','n','n','n','n','n','n','n','n','n'],
                       'catN':[1,2,3,2,3,4,3,2,3,4,3,2,1,2,1,2,3,2,3,4],
                       'catA':['a','a','b','b','c','d','a','c','c','d','a','b','c','a','d','a','b','c','a','d'],
                       'floatN':[1.2,4.3,2.3,4.3,5.3,4.3,2.4,6.5,4.5,7.6,5.6,5.6,4.8,5.2,7.4,5.4,6.5,5.7,6.8,4.5]})

phjORTable = epy.phjOddsRatio( phjTempDF = tempDF,
                               phjCaseVarName = 'caseA',
                               phjCaseValue = 'y',
                               phjRiskFactorVarName = 'catA',
                               phjRiskFactorBaseValue = 'a')

pd.options.display.float_format = '{:,.3f}'.format

print(phjORTable)
```

Output

```
caseA  y  n  odds    or       95pcCI_Woolf
catA                                      
a      3  4 0.750 1.000                ---
b      2  2 1.000 1.333  [0.1132, 15.7047]
c      2  3 0.667 0.889   [0.0862, 9.1622]
d      1  3 0.333 0.444   [0.0295, 6.7031]
```

---

### 5. phjRelativeRisk()

```python
df = phjRelativeRisk(phjTempDF,
                     phjCaseVarName,
                     phjCaseValue,
                     phjRiskFactorVarName,
                     phjRiskFactorBaseValue)
```

#### Description
This function can be used to calculate relative risk (risk ratios) and 95% confidence intervals for cross-sectional and longitudinal (cohort) studies. The function is passed a Pandas dataframe containing the data together with the name of the 'case' variable and the name of the potential risk factor variable. The function returns a Pandas dataframe based on a 2 x 2 or n x 2 contingency table together with columns containing the risk, risk ratios and 95% confidence intervals. Rows that contain a missing value in either the case variable or the risk factor variable are removed before calculations are made.

#### Function parameters
The function takes the following parameters:

1. **phjTempDF**
  * This is a Pandas dataframe that contains the data to be analysed. One of the columns should be a variable that indicates whether the row has disease (diseased) or not (healthy).

2. **phjCaseVarName**
  * Name of the variable that indicates whether the row has disease or is healthy.

3. **phjCaseValue**
  * The value used in phjCaseVarName variable to indicate disease (e.g. True, yes, 1, etc.)

4. **phjRiskFactorVarName**
  * The name of the potential risk factor to be analysed. This needs to be a categorical variable.

5. **phjRiskFactorBaseValue**
  * The level or stratum of the potential risk factor that will be used as the base level in the calculation of odds ratios.

#### Exceptions raised
None

#### Returns
Pandas dataframe containing a cross-tabulation of the disease status and risk factor varible. In addition, risk, relative risk and 95% confidence interval of the relative risk is presented.

#### Other notes
None

#### Example
An example of the function in use is given below:

```python
import pandas as pd
import epydemiology as epy

# Pretend this came from a cross-sectional study (even though it's the same example data as used for the case-control study above.
tempDF = pd.DataFrame({'caseN':[1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
                       'caseA':['y','y','y','y','y','y','y','y','n','n','n','n','n','n','n','n','n','n','n','n'],
                       'catN':[1,2,3,2,3,4,3,2,3,4,3,2,1,2,1,2,3,2,3,4],
                       'catA':['a','a','b','b','c','d','a','c','c','d','a','b','c','a','d','a','b','c','a','d'],
                       'floatN':[1.2,4.3,2.3,4.3,5.3,4.3,2.4,6.5,4.5,7.6,5.6,5.6,4.8,5.2,7.4,5.4,6.5,5.7,6.8,4.5]})

phjRRTable = epy.phjRelativeRisk( phjTempDF = tempDF,
                                  phjCaseVarName = 'caseA',
                                  phjCaseValue = 'y',
                                  phjRiskFactorVarName = 'catA',
                                  phjRiskFactorBaseValue = 'a')

pd.options.display.float_format = '{:,.3f}'.format

print(phjRRTable)
```

Output

```
caseA  y  n  risk    rr            95pcCI
catA                                     
a      3  4 0.429 1.000               ---
b      2  2 0.500 1.167  [0.3177, 4.2844]
c      2  3 0.400 0.933  [0.2365, 3.6828]
d      1  3 0.250 0.583  [0.0872, 3.9031]
```
