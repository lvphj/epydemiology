# epydemiology
Library of python code for epidemiologists – eventually.

## A. Installation
```python
pip install epydemiology as epy
```
## B. Usage

The following functions are available:

**[1. Load data from a named Excel cell range into a Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Load-data-from-a-named-Excel-cell-range-into-a-Pandas-dataframe)**

```python
myDF = epy.phjReadDataFromExcelNamedCellRange()
```

**[2. To load data from a MySQL or SQL SERVER database into a Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Load-data-from-a-MySQL-or-SQL-SERVER-database-into-a-Pandas-dataframe)**

```python
myDF = epy.phjGetDataFromDatabase()
```

**[3. To load text from a text file (e.g. a SQL query or regular expression) into a Python variable as a single string](https://github.com/lvphj/epydemiology/wiki/Load-text-from-a-text-file-(e.g.-a-SQL-query-or-regular-expression)-into-a-Python-variable-as-a-single-string)**

```python
myString = epy.phjReadTextFromFile()
```

**[4. To convert columns of binary data to a square matrix containing co-occurrences](https://github.com/lvphj/epydemiology/wiki/Convert-columns-of-binary-data-to-a-square-matrix-containing-co-occurrences)**

```python
myArr = epy.phjBinaryVarsToSquareMatrix()
```

**[5. To clean a column of UK postcodes in a Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Clean-a-column-of-UK-postcodes-in-a-Pandas-dataframe)**

```python
myDF = epy.phjCleanUKPostcodeVariable()
```

**[6. To generate a matched or unmatched case-control dataset (without replacement) from Pandas dataframes](https://github.com/lvphj/epydemiology/wiki/Generate-a-matched-or-unmatched-case-control-dataset-(without-replacement)-from-Pandas-dataframes)**

```python
myDF = epy.phjGenerateCaseControlDataset()
```

**[7. To select matched or unmatched case-control data (without replacement) from Pandas dataframes](https://github.com/lvphj/epydemiology/wiki/Generate-a-matched-or-unmatched-case-control-dataset-(without-replacement)-from-Pandas-dataframes)**

```python
myDF = epy.phjSelectCaseControlDataset()
```
**[8. To calculate and plot a series of binomial proportions using data stored in a Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Calculate-and-plot-proportions-using-data-stored-in-a-Pandas-dataframe)**

```python
myDF = epy.phjCalculateBinomialProportions()
```
**[9. To calculate and plot multinomial proportions using data stored in a Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Calculate-and-plot-proportions-using-data-stored-in-a-Pandas-dataframe)**

```python
myDF = epy.phjCalculateMultinomialProportions()
```

**[10. To calculate odds and odds ratios for case-control studies for data stored in Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Calculate-odds-and-odds-ratios-for-case-control-studies-for-data-stored-in-Pandas-dataframe)**

```python
myDF = epy.phjOddsRatio()
```

**[11. To calculate relative risks for cross-sectional or longitudinal studies for data stored in Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Calculate-relative-risks-for-cross-sectional-or-longitudinal-studies-for-data-stored-in-Pandas-dataframe)**

```python
myDF = epy.phjRelativeRisk()
```

**[12. Categorise a continuous variable using predefined breaks, quantiles or optimised break positions for data in a Pandas dataframe](https://github.com/lvphj/epydemiology/wiki/Categorise-a-continuous-variable-using-predefined-breaks,-quantiles-or-optimised-break-positions-for-data-in-a-Pandas-dataframe)**

```python
myDF = epy.phjCategoriseContinuousVariable()
```
or, if phjReturnBreaks is set to True:
```python
myDF,myBreaks = epy.phjCategoriseContinuousVariable()
```

**[13. To view a plot of log odds against mid-points of categories of a continuous variable](https://github.com/lvphj/epydemiology/wiki/View-a-plot-of-log-odds-against-mid-points-of-categories-of-a-continuous-variable-in-a-Pandas-dataframe)**

```python
myOddRatioTable = epy.phjViewLogOdds()
```
