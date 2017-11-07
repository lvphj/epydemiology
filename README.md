# epydemiology
Library of python code for epidemiologists – eventually.

## A. Installation
```python
pip install epydemiology as epy
```
## B. Usage

The following functions are available:

**1. To load data from a named Excel cell range into a Pandas dataframe**

```python
myDF = epy.phjReadDataFromExcelNamedCellRange()
```

**2. To load data from a MySQL or SQL SERVER database into a Pandas dataframe**

```python
myDF = epy.phjGetDataFromDatabase()
```

**3. To load text from a text file (e.g. a SQL query or regular expression) into a Python variable as a single string**

```python
myString = phjReadTextFromFile()
```

**4. To convert columns of binary data to a square matrix containing co-occurrences**

```python
myArr = epy.phjBinaryVarsToSquareMatrix()
```

**5. To clean a column of UK postcodes in a Pandas dataframe**

```python
myDF = epy.phjCleanUKPostcodeVariable()
```

**6. To select matched or unmatced case-control data (without replacement) from Pandas dataframes**

```python
myDF = epy.phjSelectCaseControlDataset()
```
**7. To calculate and plot a series of binomial proportions**

```python
myDF = epy.phjCalculateBinomialProportions()
```
**8. To calculate and plot multinomial proportions**

```python
myDF = epy.phjCalculateMultinomialProportions()
```

**9. To calculate odds and odds ratios for case-control studies for data stored in Pandas dataframe**

```python
myDF = epy.phjOddsRatio()
```
**10. To calculate relative risks for cross-sectional or longitudinal studies for data stored in Pandas dataframe**

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

This function can be used to import data from a named range in a Microsoft Excel workbook. The function receives the full path and filename of the Excel document, together with the name of the named cell range of interest, and returns the data as a Pandas dataframe.

#### Function parameters
1. **phjExcelPathAndFilename**

   The full path and filename of the Microsoft Excel workbook.

2. **phjExcelCellRangeName**

   The name of the cell range of interest. It is import to ensure that the name range only occurs once in the workbook.

3. **phjDatetimeFormat** (default = "%Y-%m-%d %H:%M:%S")

   The datatime format that will be used to interpret columns containing date (and time) data.

4. **phjMissingValue** (default = "missing")

   A string or code that is used to replace empty cells.

5. **phjHeaderRow** (default = False)

   Indicates whether the cell range has a header row. If so, the values in the first row of the cell range are used as the headings of the dataframe columns; otherwise, the columns are given default, generic names.

6. **phjPrintResults** (default = False)

   Print the imported results.

#### Exceptions raised

None.

#### Returns

Pandas dataframe containing data read from named cell range.

#### Other notes

None.

#### Example

An example of the function in use is given below. An Excel workbook named 'myWorkbook.xlsx' is stored on the Desktop. The workbook contains several individual worksheets, one of which contains a named cell range called 'myCellRange', the first row of which contains the names of the columns. The data can be imported into a Pandas dataframe using:

```python
# The following libraries are imported automatically but are incuded here for completeness.
import pandas as pd
import openpyxl
import epydemiology as epy

myTempDF = epy.phjReadDataFromExcelNamedCellRange(phjExcelPathAndFileName = '/Users/username/Desktop/myWorkbook.xlsx',
                                                  phjExcelCellRangeName = 'myCellRange',
                                                  phjDatetimeFormat = "%Y-%m-%d %H:%M:%S",
                                                  phjMissingValue = "missing",
                                                  phjHeaderRow = True,
                                                  phjPrintResults = False)

```
---
### 2. phjGetDataFromDatabase()

```python
df = phjGetDataFromDatabase(phjQueryPathAndFileName = None,
                            phjPrintResults = False)
```

Python function to read data from a MySQL or SQL SERVER database.

#### Description

The function is used to query MySQL or SQL SERVER databases using an SQL query that is stored as a text file. As the function runs, the user will be prompted to enter all other required parameters including server address, username and password details. A maximum of three attempts allowed to enter correct login information. The password is entered and remains securely obscured on-screen.

#### Function parameters

1. **phjQueryPathAndFilename**

   The full path and filename of the SQL text file containing the SQL query.
   
2. **phjPrintResults** (default = False)

   Print the imported results.

#### Exceptions raised

None.

#### Returns

Pandas dataframe containing data read from database.

#### Other notes

None.

#### Example

An example of the function in use is given below. If the SQL query to be used to query a SQL SERVER database is saved as a text file named 'theSQLQueryFile.mssql' on the Desktop, the function can be used to import returned data using:

```python
# The following libraries are imported automatically but are incuded here for completeness.
import re
import getpass
import pandas as pd
import pymysql
import pymssql
import epydemiology as epy

myTempDF = epy.phjQueryPathAndFilename(phjQueryPathAndFile = '/Users/username/Desktop/theSQLQueryFile.mssql',
                                       phjPrintResults = True)
```
---
### 3. phjReadTextFromFile()

```python
myStr = phjReadTextFromFile(phjFilePathAndName = None,
                            maxAttempts = 3,
                            phjPrintResults = False)
```

#### Description

This function can be used to read text from a text file.

#### Function parameters

1. **phjFilePathAndName**

   The full path and name of the text file to read. The text file does not need to end with the prefix '.txt'. This is the function that is used to read SQL queries from text files in the phjGetDataFromDatabase() function.

#### Exceptions raised

   None.

#### Returns

   A string containing the contents of the text file.

#### Other notes

   None.

#### Example

```python
myStr = phjReadTextFromFile(phjFilePathAndName = '/Users/username/Desktop/myTextFile.txt',
                            maxAttempts = 3,
                            phjPrintResults = False)


```
---
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
    Pandas dataframe

2. **phjColumnNamesList**
    A list of variable names contained in the dataframe that contains binary data.
    
3. **phjOutputFormat** (default = 'arr')
    Output format. Default is a Numpy array ('arr'). Alternative is 'df' to return a Pandas dataframe.
    
4. **phjPrintResults** (default = False)

Print verbose output during execution of scripts. If running on Jupyter-Notebook, setting ```phjPrintResults = True``` causes a lot a output and can cause problems connecting to kernel. It is recommended to set ```phjPrintResults = False``` routinely to avoid possible problems when using Jupyter-notebook.

#### Exceptions raised

None.

#### Returns

By default, function returns a Numpy array of a square matrix (phjOutputFormat = 'arr'). Matrix can be returned as a Pandas dataframe (phjOutputFormat = 'df').

#### Other notes

None.

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
---
### 5. phjCleanUKPostcodeVariable()

```python
df = phjCleanUKPostcodeVariable(phjCleanUKPostcodeVariable(phjTempDF,
                                phjRealPostcodeSer = None,
                                phjOrigPostcodeVarName = 'postcode',
                                phjNewPostcodeVarName = 'postcodeClean',
                                phjNewPostcodeStrLenVarName = 'postcodeCleanStrLen',
                                phjPostcodeCheckVarName = 'postcodeCheck',
                                phjMissingValueCode = 'missing',
                                phjMinDamerauLevenshteinDistanceVarName = 'minDamLevDist',
                                phjBestAlternativesVarName = 'bestAlternatives',
                                phjPostcode7VarName = 'postcode7',
                                phjPostcodeAreaVarName = 'postcodeArea',
                                phjSalvageOutwardPostcodeComponent = True,
                                phjCheckByOption = 'format',
                                phjDropExisting = False,
                                phjPrintResults = True)

```

Python function to clean and extract correctly formatted postcode data.

#### Description

In many situations, postcodes are added to a database field to record people's addresses. However, when entering postcodes by hand or transcribing from written notes, it is often the case that postcodes are entered incorrectly due to typing errors or because the postcode in question is not fully known. Consequently, a variable containing postcode information will contain many correct postcodes but also many incorrect or partial data points. This function seeks to extract correctly formatted postcodes and to correct some commonly occurring transcription errors in order to produce a correctly-formatted postcode. In addition, in situations where just the outward component (first half) of the postcode is recorded, the function will attempt to salvage just the outward component. Finally, the function extracts the postcode area (first 1 or 2 letters) of the postcode. The cleaned postcode (with no spaces and in 7-character format), the outward and inward components of the postcode and the postcode areas are all stored in new variables that are added to the original dataframe.

This function uses one of two methods to extract postcode information: i) checking the postcode is correctly 'formatted' using a regex; ii) comparing the postcode to a database of all known postcodes and, if the postcode does not exist, determining the most likely alternatives based on Damerau-Levenshtein distance and on the physical position of inserted or transposed characters on the keyboard.

The regex used to determine whether postcodes are correctly formatted is a modified version of a regex published at https://en.wikipedia.org/wiki/Talk:Postcodes_in_the_United_Kingdom (accessed 22 Mar 2016). (This page is also stored locally as a PDF entitled, "Talk/Postcodes in the United Kingdom - Wikipedia, the free encyclopedia".)

The function takes, as two of its arguments, a Pandas dataframe containing a column of postcode data, and the name of that postcode column. It returns the same dataframe with some additional, postcode-related columns. The additional columns returned are:

i. 'postcodeClean' (column name is user-defined through phjNewPostcodeVarName argument)

   This variable will contain the correctly formatted components of the postcode, either the whole postcode or the outward component (first half of postcode). Postcodes that are incorrectly formatted or have been entered as missing values will contain the missing value code (e.g. 'missing').

ii. 'postcodeFormatCheck' (column name is user-defined through phjPostcodeFormatCheckVarName argument)

   This is a binary variable that contains True if a correctly formatted postcode component can be extracted, either the whole postcode or the outward component only. Otherwise, it contains False.

iii. 'postcode7' (column name is user-defined through the phjPostcode7VarName argument)

   This variable contains correctly formatted complete postcodes in 7-character format. For postcodes that contain 5 letters, the outward and inward components will be separated by 2 spaces; for postcodes that contain 6 letters, the outward and inward components will be separated by 1 space; and postcodes that contain 7 letters will contain no spaces. This format of postcodes is often used in postcode lookup tables.

iv. 'postcodeOutward' (defined as a group name in the regular expression and, therefore, not user-definable)

   This variable contains the outward component of the postcode (first half of postcode). It is possible that this variable may contain a correctly-formatted postcode string (2 to 4 characters) whilst the variable containing the inward postcode string contains the missing vaue code. 

v. 'postcodeInward' (defined as a group name in the regular expression and, therefore, not user-definable)

   This variable contains the inward component of the postcode (second half of postcode). It is possible that this variable may contain a missing value whilst the postcodeOutward variable contains a correctly-formatted postcode string (2 to 4 characters).

vi. 'phjPostcodeArea' (column name is user-defined through the phjPostcodeAreaVarName argument)

   This variable contains the postcode area (first one or two letters) taken from correctly formatted outward postcode components.


The function proceeds as follows:

a. Postcodes data is cleaned by removing all spaces and punctuation marks and converting all letters to uppercase. Missing values and strings that cannot possibly be a postcode (e.g. all numeric data) are converted to the missing value code. The cleaned strings are stored temporarily in the postcodeClean variable.

b. Correctly formatted postcodes (in postcodeClean column) are identified using the regular expression and the postcodeFormatCheck is set to True. Outward and inward components are extracted and stored in the relevant columns.

c. Postcodes that are incorrectly formatted undergo an error-correction step where common typos and mis-transcriptions are corrected. After this process, the format of the corrected postcode is checked again using the regex and the postcodeFormatCheck variable set to True if necessary. Outward and inward components are extracted and stored in the relevant columns.

d. If the phjSalvageOutwardPostcodeComponent arugment is set to True (default), the function attempts to salvage just the outward postcode component. The postcode string in the postcodeClean variable are tested using the outward component of the regex to determine if the first 2 to 4 characters represent a correctly formatted outward component of a postcode. If so, postcodeFormatCheck is set to True and the partial string is extracted and stored in the postcodeOutward column.

e. Common typos and mis-transcriptions are corrected once again and the string tested against the regex to determine if the first 2 to 4 characters represent a correctly formatted outward component of a postcode. If so, postcodeFormatCheck is set to True and the partial string is extracted and stored in the postcodeOutward column.

f. For any postcode strings that have not been identified as a complete or partial match to the postcode regex, the postcodeClean variable is set to the missing value code.

g. The postcode area is extracted from the outwardPostcode variable and stored in the postcodeArea variable.

h. The function returns the dataframe containing the additional columns.


#### Function parameters

The function takes the following parameters:

1. **phjTempDF**

   Pandas dataframe containing a variable that contains postcode information.
  
2. **phjRealPostcodeSer** (default = None)

   If the postcodes are to be compared to real postcodes, this variable should refer to a Pandas Series of genuine postcodes.

3. **phjOrigPostcodeVarName** (default = 'postcode')

   The name of the variable that contains postcode information.

4. **phjNewPostcodeVarName** (default = 'postcodeClean')

   The name of the variable that the function creates that will contain 'cleaned' postcode data. The postcodes stored in this column will contain no whitespace. Therefore, A1 2BC will be entered as A12BC. Also, the 'cleaned' postcode may only be the outward component if that is the only corrected formatted data. If the use wants to view only complete postcodes, use phjPostcode7VarName. Strings where no valid postcode data has been extracted will be stored as missing value string.

5. **phjNewPostcodeStrLenVarName** (default = 'postcodeCleanStrLen')

   Name of the variable that will be created to contain the length of the postcode.
  
6. **phjPostcodeCheckVarName** (default = 'postcodeCheck')

   A binary variable that the function will create that indicates whether the whole postcode (or, if only 2 to 4 characters are entered, the outward component of the postcode) is either correctly formatted or matches the list of real postcodes supplied, depending on what what requested.

7. **phjMissingValueCode** (default = 'missing')

   String used to indicate a missing value. This can not be np.nan because DataFrame.update() function does not undate NaN values.
  
8. **phjMinDamerauLevenshteinDistanceVarName** (default = 'minDamLevDist')

   Name of variable that will be created to contain the DL distance.
  
9. **phjBestAlternativesVarName** (default = 'bestAlternatives')

   Name of variable that will be created to contain best (or closest matching) postcodes from the list of real postcodes.
  
10. **phjPostcode7VarName** (default = 'postcode7')

   The name of the variable that the function creates that will contain 'cleaned' postcode data in 7-character format. Postcodes can contain 5 to 7 characters. In those postcodes that consist of 5 characters, the outward and inward components will be separated by 2 spaces, in those postcodes that consist of 6 characters, the outward and inward components will be separated by 1 spaces, and in those postcodes that consist of 7 characters there will be no spaces. This format is commonly used in lookup tables that link postcodes to other geographical information.

11. **phjPostcodeAreaVarName** (default = 'postcodeArea')

   The name of the variable that the function creates that will contain the postcode area (the first 1, 2 or, in very rare cases, 3 letters).

12. **phjSalvageOutwardPostcodeComponent** (default = True)

   Indicates whether user wants to attempt to salvage some outward postcode components from postcode strings.
  
13. **phjCheckByOption** (default = 'format')

   Select method to use to check postcodes. The default is 'format' and checks the format of the postcode using a regular expression. The alternative is 'dl' which calculates the Damarau-Levenshtein distance from each postcode in the list of supplied postcodes and chooses the closest matches based on the DL distance and the disctance of inserted or trasposed characters based on physical distance on a standard QWERTY keyboard.
  
14. **phjDropExisting** (default = False)

   If set to True, the function will automatically drop any pre-existing columns that have the same name as those columns that need to be created. If set to False, the function will halt.

15. **phjPrintResults** (default = False)

   If set to True, the function will print information to screen as it proceeds.

#### Exceptions raised

None.

#### Returns

By default, function returns the original dataframe with added columns containing postcode data.

#### Other notes

None.

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
                                              phjRealPostcodeSer = None,
                                              phjOrigPostcodeVarName = 'postcode',
                                              phjNewPostcodeVarName = 'pcdClean',
                                              phjNewPostcodeStrLenVarName = 'pcdCleanStrLen',
                                              phjPostcodeCheckVarName = 'pcdFormatCheck',
                                              phjMissingValueCode = 'missing',
                                              phjMinDamerauLevenshteinDistanceVarName = 'minDamLevDist',
                                              phjBestAlternativesVarName = 'bestAlternatives',
                                              phjPostcode7VarName = 'pcd7',
                                              phjPostcodeAreaVarName = 'pcdArea',
                                              phjSalvageOutwardPostcodeComponent = True,
                                              phjCheckByOption = 'format',
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
---
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

   Pandas dataframe containing list of cases.
  
2. **phjPotentialControlsDF**

   Pandas dataframe containing a list of potential control cases.
  
3. **phjUniqueIdentifierVarName**

   Name of variable that acts as a unique identifier (e.g. consulations ID number would be a good example). N.B. In some cases, the consultation number is not unique but has been entered several times in the database, sometimes in very quick succession (ms). Data must be cleaned to ensure that the unique identifier variable is, indeed, unique.
  
4. **phjMatchingVariablesList** (Default = None)

   List of variable names for which the cases and controls should be matched. Must be a list. The default is None.
  
5. **phjControlsPerCaseInt** (Default = 1)

   Number of controls that should be selected per case.
  
6. **phjPrintResults** (Default= False)

   Print verbose output during execution of scripts. If running on Jupyter-Notebook, setting PrintResults = True causes a lot a output and can cause problems connecting to kernel.

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
### 7. phjCalculateBinomialProportions()
```python
df = phjCalculateBinomialProportions(phjTempDF,
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
                                     phjPrintResults = False)
```
### 8. phjCalculateMultinomialProportions()
```python
df = phjCalculateMultinomialProportions(phjTempDF,
                                        phjCategoryVarName = None,
                                        phjCategoriesToPlotList = 'all',
                                        phjGroupVarName = None,
                                        phjMissingValue = 'missing',
                                        phjMultinomialConfIntMethod = 'goodman',
                                        phjAlpha = 0.05,
                                        phjPlotRelFreq = True,
                                        phjGroupsToPlotList = 'all',
                                        phjGraphTitle = None,
                                        phjPrintResults = False)
```

#### Description

The above two functions – ``` phjCalculateBinomialProportions() and phjCalculateMultinomialProportions() ``` – are closely related and will be discussed and described together.

The functions can be used to rapidly summarise and visualise two common-encountered (at least, in my research) types of data. The first summarises data which consists of rows of records (representing individuals) and a series of binomial (dummy-esque) variables indicating whether a characteristic is present or absent (see below). These are not true dummy variables because categories are not necessarily mutually exclusive and each variable is considered as an individual characteristic. The confidence intervals for each category are calculated as individual binomial intervals (using StatsModels functions).

The second data structure consists of rows of data (representing individuals) and a single variable which contains numerous categories. In this case, all the categories are mutually exclusive. The proportions (or relative frequencies) are calculated for each category level and the confidence intervals are calculated as multinomial intervals (using StatsModels functions).

The series of binomial data might take the form shown on the left whilst the multinomial dataset might take the form shown on the right below:

```
Binomial data structure                                   Multinomial data structure
------------------------------------------------          ------------------------------
| id |    group  |       A |       B |       C |          | id |    group  |  category |
|----|-----------|---------|---------|---------|          |----|-----------|-----------|
|  1 |     case  |     yes |      no |     yes |          |  1 |     case  |    np.nan |
|  2 |     case  |     yes |  np.nan |     yes |          |  2 |     case  |   spaniel |
|  3 |  control  |      no | missing |     yes |          |  3 |     case  |   missing |
|  4 |     case  |      no |     yes |  np.nan |          |  4 |  control  |   terrier |
|  5 |  control  |      no |     yes |      no |          |  5 |  control  |    collie |
|  6 |  control  |      no |     yes |     yes |          |  6 |     case  |  labrador |
|  7 |     case  |      no |     yes |     yes |          |  7 |     case  |  labrador |
|  8 |     case  |     yes |      no |     yes |          |  8 |     case  |    collie |
|  9 |  control  | missing |      no |      no |          |  9 |  control  |   spaniel |
| 10 |     case  |     yes |      no |      no |          | 10 |  control  |   spaniel |
------------------------------------------------          | 11 |  control  |  labrador |
                                                          | 12 |  control  |    collie |
                                                          | 13 |     case  |   terrier |
                                                          | 14 |     case  |   terrier |
                                                          | 15 |     case  |   terrier |
                                                          | 16 |  control  |    collie |
                                                          | 17 |  control  |  labrador |
                                                          | 18 |  control  |  labrador |
                                                          | 19 |  control  |  labrador |
                                                          | 20 |     case  |   spaniel |
                                                          | 21 |     case  |   spaniel |
                                                          | 22 |     case  |    collie |
                                                          | 23 |     case  |    collie |
                                                          | 24 |     case  |    collie |
                                                          | 25 |   np.nan  |   terrier |
                                                          | 26 |   np.nan  |   spaniel |
                                                          ------------------------------

```

In both datasets, missing values can be entered either as np.nan or as a missing value string such as 'missing' which is then defined when the function is called.

These example datasets can be produced using the following Python code:

```python
import numpy as np
import pandas as pd

binomDataDF = pd.DataFrame({'id':[1,2,3,4,5,6,7,8,9,10],
                            'group':['case','case','control','case','control','control','case','case','control','case'],
                            'A':['yes','yes','no','no','no','no','no','yes','missing','yes'],
                            'B':['no',np.nan,'missing','yes','yes','yes','yes','no','no','no'],
                            'C':['yes','yes','yes',np.nan,'no','yes','yes','yes','no','no']})

multinomDataDF = pd.DataFrame({'id':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26],
                               'group':['case','case','case','control','control','case','case','case','control','control','control','control','case','case','case','control','control','control','control','case','case','case','case','case',np.nan,np.nan],
                               'category':[np.nan,'spaniel','missing','terrier','collie','labrador','labrador','collie','spaniel','spaniel','labrador','collie','terrier','terrier','terrier','collie','labrador','labrador','labrador','spaniel','spaniel','collie','collie','collie','terrier','spaniel']})
```

The output summary tables in each case would be very similar:

```
    Summary table for multinomial proportions
    
    |---------|---------------|---------------|---------------|---------------|
    |         |    case_count | control_count |     case_prop |  control_prop |
    |---------|---------------|---------------|---------------|---------------|
    | spaniel |               |               |               |               |
    |---------|---------------|---------------|---------------|---------------|
    | terrier |               |               |               |               |
    |---------|---------------|---------------|---------------|---------------|
    | labrador|               |               |               |               |
    |---------|---------------|---------------|---------------|---------------|
    | collie  |               |               |               |               |
    |---------|---------------|---------------|---------------|---------------|
    
    * The 'count' columns give the absolute counts.
      The 'prop' columns give the proportion of the total.
    
    
    Summary table for binomial proportions
    
    |-----|---------------|-----------------|---------------|---------------|---------------|---------------|
    |     |  case_success | control_success |    case_total | control_total |     case_prop |  control_prop |
    |-----|---------------|-----------------|---------------|---------------|---------------|---------------|
    |   A |               |                 |               |               |               |               |
    |-----|---------------|-----------------|---------------|---------------|---------------|---------------|
    |   B |               |                 |               |               |               |               |
    |-----|---------------|-----------------|---------------|---------------|---------------|---------------|
    |   C |               |                 |               |               |               |               |
    |-----|---------------|-----------------|---------------|---------------|---------------|---------------|
    
    * The 'success' columns give the number of 'successes' in each variable.
      The 'total' columns give the total number of rows (missing values excluded) for each variable.
      The 'prop' columns give the proportion of successes.
```

The confidence intervals (either binomial or multinomial) are added to the table as separate columns containing lower and upper limits.

And the data would be plotted in a similar fashion (although the method used to calculate the error bars would be different).

```
     R  |           |-|                                 |           |-|             
     e  |           |/|-|                               |           |/|-|           |/| case
     l  |     |-|   |/| |           |-|               P |     |-|   |/| |           
        |     | |   |/| |           |/|-|             r |     | |   |/| |           | | control
     F  |   |-| |   |/| |     |-|   |/| |       OR    o |   |-| |   |/| |     |-|   
     r  |   |/| |   |/| |   |-| |   |/| |             p |   |/| |   |/| |   |-| |   
     e  |   |/| |   |/| |   |/| |   |/| |               |   |/| |   |/| |   |/| |   
     q  |-----------------------------------            |---------------------------
             spn     ter     lab     col                      A       B       C

```

#### Function parameters

**phjCalculateBinomialProportions() function**

The phjCalculateBinomialProportions() function takes the following parameters:

1. **phjTempDF**

   The Pandas dataframe containing the data to be analysed. The dataframe does not need to be sliced before use because the data columns that need to be used are defined in the function arguments.

2. **phjColumnsList = None**

   A list of the columns that need to be analyses. Each of these columns should be binary variables and should contain only binary data. Missing values (either in the form of a specified missing value or a np.nan value will be removed before analysis).

3. **phjSuccess = 'yes'**

   The text string or value that is used to indicate a positive value or a 'success'. The default assumes that data will be coded as 'yes' or 'no'.

4. **phjGroupVarName = None**

   It is likely that some analysis will need to summarise data over two distinct categories (e.g. 'case' and 'control' data may be summarised separately). This varialble should contain the column heading for the variable that defines group membership. The default is None. If phjGroupVarName is None, the whole dataset is analysed as a single group.

5. **phjMissingValue = 'missing'**

   The text string or value that indicates a success.

6. **phjBinomialConfIntMethod = 'normal'**

   This argument defines the method to be used to calculate the binomial confidence intervals. The options available are those that can be handled by the statsmodel.proporotions() method. The default is 'normal' but the full list of options (taken from the statsmodels website) are:
   1. `normal` : asymptotic normal approximation
   2. `agresti_coull` : Agresti-Coull interval
   3. `beta` : Clopper-Pearson interval based on Beta distribution
   4. `wilson` : Wilson Score interval
   5. `jeffreys` : Jeffreys Bayesian Interval
   6. `binom_test` : experimental, inversion of binom_test

7. **phjAlpha = 0.05**

   The desired value for alpha; the default is 0.05 (which leads to the calculation of 95% confidence intervals.

8. **phjPlotProportions = True**

   Determines whether a bar chart (with errors bars) is plotted.

9. **phjGroupsToPlotList = 'all'**

   The data may be calculated for numerous groups but it may not be desired for the plot to display all groups. This argument is a list of groups which should be displayed in the plot.

10. **phjSortProportions = False**

   If only a single group is plotted, this argument indicates whether the columns should be sorted. Default is 'False' but other options are 'asc' or desc'.

11. **phjGraphTitle = None**

   The title of the graph.

12. **phjPrintResults = False**

   Indicates whehter the results should be printed to screed as the function progresses.


**phjCalculateMultinomialProportions() function**

The phjCalculateMultinomialProportions() function takes the following parameters:

1. **phjTempDF**

   The Pandas dataframe containing the data to be analysed. The dataframe does not need to be sliced before use because the data columns that need to be used are defined in the function arguments.

2. **phjCategoryVarName = None**


3. **phjGroupVarName = None**


4. **phjMissingValue = 'missing'**


5. **phjMultinomialConfIntMethod = 'goodman'**


6. **phjAlpha = 0.05**


7. **phjPlotRelFreq = True**


8. **phjCategoriesToPlotList = 'all'**


9. **phjGroupsToPlotList = 'all'**


10. **phjGraphTitle = None**


11. **phjPrintResults = False**


#### Exceptions raised

None

#### Returns

Pandas dataframe containing a table of proportions and confidence intervals.

#### Other notes

None

#### Example

An example of the function in use is given below:

---
### 9. phjOddsRatio()

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

   This is a Pandas dataframe that contains the data to be analysed. One of the columns should be a variable that indicates whether the row is a case or a control.

2. **phjCaseVarName**

   Name of the variable that indicates whether the row is a case or a control.

3. **phjCaseValue**

   The value used in phjCaseVarName variable to indicate a case (e.g. True, yes, 1, etc.)

4. **phjRiskFactorVarName**

   The name of the potential risk factor to be analysed. This needs to be a categorical variable.

5. **phjRiskFactorBaseValue**

   The level or stratum of the potential risk factor that will be used as the base level in the calculation of odds ratios.

#### Exceptions raised

None.

#### Returns

Pandas dataframe containing a cross-tabulation of the case and risk factor varible. In addition, odds, odds ratios and 95% confidence interval (Woolf) of the odds ratio is presented.

#### Other notes

None.

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
### 10. phjRelativeRisk()

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

   This is a Pandas dataframe that contains the data to be analysed. One of the columns should be a variable that indicates whether the row has disease (diseased) or not (healthy).

2. **phjCaseVarName**

   Name of the variable that indicates whether the row has disease or is healthy.

3. **phjCaseValue**

   The value used in phjCaseVarName variable to indicate disease (e.g. True, yes, 1, etc.)

4. **phjRiskFactorVarName**

   The name of the potential risk factor to be analysed. This needs to be a categorical variable.

5. **phjRiskFactorBaseValue**

   The level or stratum of the potential risk factor that will be used as the base level in the calculation of odds ratios.

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
---
