# epydemiology
Library of python code for epidemiologists – eventually.

## A. Installation
```python
pip install epydemiology as epy
```
## B. Usage

The following functions are available:
1. To load data from a named Excel cell range into a Pandas dataframe

```python
myDF = epy.phjReadDataFromExcelNamedCellRange()
```

2. To load data from a MySQL or SQL SERVER database into a Pandas dataframe

```python
myDF = epy.phjGetDataFromDatabase()
```

3. To load text from a text file (e.g. a SQL query or regular expression) into a Python variable as a single string

```python
myString = phjReadTextFromFile()
```

4. To convert columns of binary data to a square matrix containing co-occurrences

```python
myArr = epy.phjBinaryVarsToSquareMatrix()
```

5. To clean a column of UK postcodes in a Pandas dataframe

```python
myDF = epy.phjCleanUKPostcodeVariable()
```

6. To select matched or unmatced case-control data (without replacement) from Pandas dataframes

```python
myDF = epy.phjSelectCaseControlDataset()
```
7. To calculate odds and odds ratios for case-control studies for data stored in Pandas dataframe

```python
myDF = epy.phjOddsRatio()
```
8. To calculate relative risks for cross-sectional or longitudinal studies for data stored in Pandas dataframe

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



### 3. phjReadTextFromFile()

```python
myStr = phjReadTextFromFile(phjFilePathAndName = None,
                            maxAttempts = 3,
                            phjPrintResults = False)
```

#### Description


#### Function parameters


#### Exceptions raised


#### Returns


#### Other notes


#### Example










### 4. phjBinaryVarsToSquareMatrix()

```python
arr = phjBinaryVarsToSquareMatrix(phjDataDF,
                                  phjColumnNamesList,
                                  phjOutputFormat = 'arr',
                                  phjPrintResults = False)
```

Function to produce a Numpy array from a group of binary variables to show co-occurrence.
#### Description
This function takes a number of variables containing binary data and returns a Numpy array representing a square matrix that shows co-occurrence of positive variables.

#### Function parameters

1. **phjDataDF**
    * Pandas dataframe

2. **phjColumnNamesList**
    * A list of variable names contained in the dataframe that contains binary data.
    
3. **phjOutputFormat** (Default = 'arr')
    * Output format. Default is a Numpy array ('arr'). Alternative is 'df' to return a Pandas dataframe.
    
4. **phjPrintResults** (Default = False.)
  * Print verbose output during execution of scripts. If running on Jupyter-Notebook, setting PrintResults = True causes a lot a output and can cause problems connecting to kernel.

#### Exceptions raised
None

#### Returns
By default, function returns a Numpy array of a square matrix (phjOutputFormat = 'arr'). Matrix can be returned as a Pandas dataframe (phjOutputFormat = 'df').

#### Other notes
None

#### Example

```python
import pandas as pd

rawDataDF = pd.DataFrame({'a':[0,1,1,1,0,0,1,0],
                          'b':[1,1,0,0,1,0,0,1],
                          'c':[0,0,1,0,1,1,1,1],
                          'd':[1,0,0,0,1,0,0,0],
                          'e':[1,0,0,0,0,1,0,0]})

columns = ['a','b','c','d','e']

phjMatrix = phjBinaryVarsToSquareMatrix(phjDataDF = rawDataDF,
                                        phjColumnNamesList = columns,
                                        phjOutputFormat = 'arr',
                                        phjPrintResults = False)
                                        
print(phjMatrix)
```

Output:

```
[[1 1 2 0 0]
 [1 0 2 2 1]
 [2 2 0 1 1]
 [0 2 1 0 1]
 [0 1 1 1 0]]
```


### 5. phjCleanUKPostcodeVariable()

```python
df = phjCleanUKPostcodeVariable(phjTempDF,
                                phjOrigPostcodeVarName = 'postcode',
                                phjNewPostcodeVarName = 'postcodeClean',
                                phjPostcodeFormatCheckVarName = 'postcodeFormatCheck',
                                phjPostcode7VarName = 'postcode7',
                                phjPostcodeAreaVarName = 'postcodeArea',
                                phjDropExisting = False,
                                phjPrintResults = False)

```

Python function to clean and extract correctly formatted postcode data.
#### Description
In many situations, postcodes are added to a database field to record people's addresses. However, when entering postcodes by hand or transcribing from written notes, it is often the case that postcodes are entered incorrectly due to typing errors or because the postcode in question is not fully known. Consequently, a variable containing postcode information will contain many correct postcodes but also many incorrect or partial data points. This function seeks to extract correctly formatted postcodes and to correct some commonly occurring transcription errors in order to produce a correctly-formatted postcode. In addition, in situations where just the outward component (first half) of the postcode is recorded, the function will attempt to salvage just the outward component. Finally, the function extracts the postcode area (first 1 or 2 letters) of the postcode. The cleaned postcode (with no spaces and in 7-character format), the outward and inward components of the postcode and the postcode areas are all stored in new variables that are added to the original dataframe.

The names of the variables that will be created to contain the outward and inward components of the postcode are 'postcodeOutward' and 'postcodeInward'. These names are the names of the groups defined by the regular expression and are not user-definable.

The regex used to determine whether postcodes are correctly formatted is a modified regex based on a regex published at https://en.wikipedia.org/wiki/Talk:Postcodes_in_the_United_Kingdom (accessed 22 Mar 2016). (This page is also stored locally as a PDF entitled, "Talk/Postcodes in the United Kingdom - Wikipedia, the free encyclopedia".)

NOTE: This function does not check entered postcodes against a database of actual postcodes. In merely checks that the *format* of the entered postcode is correct. So, for example, AB12 3CD is a correctly formatted postcode but it may or may not actually exist.
  
#### Function parameters
The function takes the following parameters:

1. **phjTempDF**
  * Pandas dataframe containing a variable that contains postcode information.

2. **phjOrigPostcodeVarName** (default = 'postcode')
  * The name of the variable that contains postcode information.

3. **phjNewPostcodeVarName** (default = 'postcodeClean')
  * The name of the variable that the function creates that will contain 'cleaned' postcode data. The postcodes stored in this column will contain no whitespace. Therefore, A1 2BC will be entered as A12BC. Also, the 'cleaned' postcode may only be the outward component if that is the only corrected formatted data. If the use wants to view only complete postcodes, use phjPostcode7VarName. Strings where no valid postcode data has been extracted will be stored as missing value string.

4. **phjPostcodeFormatCheckVarName** (default = ' postcodeFormatCheck')
  * A binary variable that the function will create that indicates whether the whole postcode (or, if only 2 to 4 characters are entered, the outward component of the postcode) is correctly formatted.

5. **phjMissingValueCode** (default = 'missing')
  * String used to indicate a missing value. This can not be np.nan because DataFrame.update() function does not undate NaN values.
  
6. **phjPostcode7VarName** (default = 'postcode7')
  * The name of the variable that the function creates that will contain 'cleaned' postcode data in 7-character format. Postcodes can contain 5 to 7 characters. In those postcodes that consist of 5 characters, the outward and inward components will be separated by 2 spaces, in those postcodes that consist of 6 characters, the outward and inward components will be separated by 1 spaces, and in those postcodes that consist of 7 characters there will be no spaces. This format is commonly used in lookup tables that link postcodes to other geographical information.

7. **phjPostcodeAreaVarName** (default = 'postcodeArea')
  * The name of the variable that the function creates that will contain the postcode area (the first 1, 2 or, in very rare cases, 3 letters).

8. **phjSalvageOutwardPostcodeComponent** (default = True)
  * Indicates whether user wants to attempt to salvage some outward postcode components from postcode strings.
  
9. **phjDropExisting** (default = False)
  * If set to True, the function will automatically drop any pre-existing columns that have the same name as those columns that need to be created. If set to False, the function will halt.

10. **phjPrintResults** (default = False)
  * If set to True, the function will print information to screen as it proceeds.

#### Exceptions raised
None

#### Returns
By default, function returns the original dataframe with added columns containing postcode data.

#### Other notes
None

#### Example

```python
# Create a test dataframe that contains a postcode variable and some other empty variables
# that have the same names as the new variables that will be created. Setting the 'phjDropExisting'
# variable to true will automatically drop pre-existing variables before running the function.
# Some of the variables in the test dataframe are not duplicated and are present to show that the
# function preserves those variables in tact.

import numpy as np
import pandas as pd
import re

# Create test dataframe
myTestPostcodeDF = pd.DataFrame({'postcode': ['NP45DG',
                                              'CH647TE',
                                              'CH5 4HE',
                                              'GIR 0AA',
                                              'NOT NOWN',
                                              'GIR0AB',
                                              'NOR12A',
                                              'no idea',
                                              'W1A 1AA',
                                              'missin',
                                              'NP4  OGH',
                                              'P012 OLL',
                                              'p01s',
                                              'ABCD',
                                              '',
                                              'ab123cd',
                                              'un-known',
                                              'B1    INJ',
                                              'AB123CD',
                                              'No idea what the postcode is',
                                              '    ???NP4-5DG_*#   '],
                                 'pcdClean': np.nan,
                                 'pcd7': np.nan,
                                 'postcodeOutward': np.nan,
                                 'someOtherCol': np.nan})

# Run function to extract postcode data
print('\nStart dataframe\n===============\n')
print(myTestPostcodeDF)
print('\n')

myTestPostcodeDF = phjCleanUKPostcodeVariable(phjTempDF = myTestPostcodeDF,
                                              phjOrigPostcodeVarName = 'postcode',
                                              phjNewPostcodeVarName = 'pcdClean',
                                              phjPostcodeFormatCheckVarName = 'pcdFormatCheck',
                                              phjMissingValueCode = 'missing',
                                              phjPostcode7VarName = 'pcd7',
                                              phjPostcodeAreaVarName = 'pcdArea',
                                              phjSalvageOutwardPostcodeComponent = True,
                                              phjDropExisting = True,
                                              phjPrintResults = True)

print('\nReturned dataframe\n==================\n')
print(myTestPostcodeDF)

```
```
OUTPUT
======

Start dataframe
===============

    pcd7  pcdClean                      postcode  postcodeOutward  \
0    NaN       NaN                        NP45DG              NaN   
1    NaN       NaN                       CH647TE              NaN   
2    NaN       NaN                       CH5 4HE              NaN   
3    NaN       NaN                       GIR 0AA              NaN   
4    NaN       NaN                      NOT NOWN              NaN   
5    NaN       NaN                        GIR0AB              NaN   
6    NaN       NaN                        NOR12A              NaN   
7    NaN       NaN                       no idea              NaN   
8    NaN       NaN                       W1A 1AA              NaN   
9    NaN       NaN                        missin              NaN   
10   NaN       NaN                      NP4  OGH              NaN   
11   NaN       NaN                      P012 OLL              NaN   
12   NaN       NaN                          p01s              NaN   
13   NaN       NaN                          ABCD              NaN   
14   NaN       NaN                                            NaN   
15   NaN       NaN                       ab123cd              NaN   
16   NaN       NaN                      un-known              NaN   
17   NaN       NaN                     B1    INJ              NaN   
18   NaN       NaN                       AB123CD              NaN   
19   NaN       NaN  No idea what the postcode is              NaN   
20   NaN       NaN              ???NP4-5DG_*#                 NaN   

    someOtherCol  
0            NaN  
1            NaN  
2            NaN  
3            NaN  
4            NaN  
5            NaN  
6            NaN  
7            NaN  
8            NaN  
9            NaN  
10           NaN  
11           NaN  
12           NaN  
13           NaN  
14           NaN  
15           NaN  
16           NaN  
17           NaN  
18           NaN  
19           NaN  
20           NaN  


Column 'pcdClean' needs to be added to the dataframe but the variable already exists; the pre-existing column has been reset.
Column 'pcd7' needs to be added to the dataframe but the variable already exists; the pre-existing column has been reset.
Column 'postcodeOutward' needs to be added to the dataframe but the variable already exists; the pre-existing column has been reset.
                        postcode pcdClean pcdFormatCheck     pcd7
0                         NP45DG   NP45DG           True  NP4 5DG
1                        CH647TE  CH647TE           True  CH647TE
2                        CH5 4HE   CH54HE           True  CH5 4HE
3                        GIR 0AA   GIR0AA           True  GIR 0AA
4                       NOT NOWN  missing          False      NaN
5                         GIR0AB   GIR0AB          False      NaN
6                         NOR12A   NOR12A           True  NOR 12A
7                        no idea   NO1DEA          False      NaN
8                        W1A 1AA   W1A1AA           True  W1A 1AA
9                         missin  missing          False      NaN
10                      NP4  OGH   NP40GH           True  NP4 0GH
11                      P012 OLL  PO120LL           True  PO120LL
12                          p01s     PO15          False      NaN
13                          ABCD     ABCD          False      NaN
14                                missing          False      NaN
15                       ab123cd  AB123CD          False      NaN
16                      un-known  missing          False      NaN
17                     B1    INJ    B11NJ           True  B1  1NJ
18                       AB123CD  AB123CD          False      NaN
19  No idea what the postcode is  missing          False      NaN
20              ???NP4-5DG_*#      NP45DG           True  NP4 5DG

Returned dataframe
==================

                        postcode  someOtherCol pcdClean pcdFormatCheck  \
0                         NP45DG           NaN   NP45DG           True   
1                        CH647TE           NaN  CH647TE           True   
2                        CH5 4HE           NaN   CH54HE           True   
3                        GIR 0AA           NaN   GIR0AA           True   
4                       NOT NOWN           NaN  missing          False   
5                         GIR0AB           NaN  missing          False   
6                         NOR12A           NaN   NOR12A           True   
7                        no idea           NaN  missing          False   
8                        W1A 1AA           NaN   W1A1AA           True   
9                         missin           NaN  missing          False   
10                      NP4  OGH           NaN   NP40GH           True   
11                      P012 OLL           NaN  PO120LL           True   
12                          p01s           NaN     PO15           True   
13                          ABCD           NaN  missing          False   
14                                         NaN  missing          False   
15                       ab123cd           NaN     AB12           True   
16                      un-known           NaN  missing          False   
17                     B1    INJ           NaN    B11NJ           True   
18                       AB123CD           NaN     AB12           True   
19  No idea what the postcode is           NaN  missing          False   
20              ???NP4-5DG_*#              NaN   NP45DG           True   

       pcd7 postcodeOutward postcodeInward pcdArea  
0   NP4 5DG             NP4            5DG      NP  
1   CH647TE            CH64            7TE      CH  
2   CH5 4HE             CH5            4HE      CH  
3   GIR 0AA             GIR            0AA     GIR  
4       NaN             NaN            NaN     NaN  
5       NaN             NaN            NaN     NaN  
6   NOR 12A             NOR            12A     NOR  
7       NaN             NaN            NaN     NaN  
8   W1A 1AA             W1A            1AA       W  
9       NaN             NaN            NaN     NaN  
10  NP4 0GH             NP4            0GH      NP  
11  PO120LL            PO12            0LL      PO  
12      NaN            PO15            NaN      PO  
13      NaN             NaN            NaN     NaN  
14      NaN             NaN            NaN     NaN  
15      NaN            AB12            NaN      AB  
16      NaN             NaN            NaN     NaN  
17  B1  1NJ              B1            1NJ       B  
18      NaN            AB12            NaN      AB  
19      NaN             NaN            NaN     NaN  
20  NP4 5DG             NP4            5DG      NP

```


### 6. phjSelectCaseControlDataset()

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

### 7. phjOddsRatio()

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

### 8. phjRelativeRisk()

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
