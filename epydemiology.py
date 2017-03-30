import numpy as np
import pandas as pd
import math



def phjCaseVarCheck(phjTempDF,
                    phjCaseVarName):
    
    try:
        assert phjCaseVarName in phjTempDF.columns, 'The selected name for the case variable does not exist in the dataframe.'
        phjCheckPassed = True
        
        # Check that case variable contains 2 and only 2 levels
        try:
            assert phjTempDF[phjCaseVarName].nunique() == 2, 'The selected variable must contain only 2 levels, one representing a case and one a control.'
            phjCheckPassed = True
            
        except AssertionError as e:
            print(e)
            phjCheckPassed = False

    except AssertionError as e:
        print(e)
        phjCheckPassed = False
    
    return phjCheckPassed



def phjCaseFirst(phjTempDF,
                 phjCaseValue):
    
    # Creates a list with case value first. This can be used to order the dataframe columns
    phjCaseOrder = phjTempDF.columns.tolist()
    
    phjCaseOrder.remove(phjCaseValue)
    
    phjNewCaseOrder = [phjCaseValue] + phjCaseOrder
    
    # Return a list containing cases and controls with cases column coming first
    return phjNewCaseOrder
    
    

def phjValueCheck(phjTempDF,
                  phjVarName,
                  phjValue):
    try:
        assert phjValue in phjTempDF[phjVarName].unique(),'The value {0} does not exist in variable {1}.'.format(phjValue,phjVarName)
        phjCheckPassed = True
        
    except AssertionError as e:
        print(e)
        phjCheckPassed = False
        
    return phjCheckPassed



def phjOddsRatio(phjTempDF,
                 phjCaseVarName,
                 phjCaseValue,
                 phjRiskFactorVarName,
                 phjRiskFactorBaseValue):
    
    # Data to use - remove rows that have a missing value
    phjTempDF = phjTempDF[[phjCaseVarName,phjRiskFactorVarName]].dropna(axis = 0, how = 'any').reset_index(drop = True)
    
    # Check cases variable occurs and there are only 2 categories
    phjCheckPassed = phjCaseVarCheck(phjTempDF = phjTempDF,
                                     phjCaseVarName = phjCaseVarName)
    
    # Check values occur in variables
    for i,j in [[phjCaseValue,phjCaseVarName],[phjRiskFactorBaseValue,phjRiskFactorVarName]]:
        phjCheckPassed = phjValueCheck(phjTempDF = phjTempDF,
                                       phjVarName = j,
                                       phjValue = i)
    
    if phjCheckPassed:
        # Calculated univariable contingency table with risk factor levels as index and
        # cases and controls as columns.
        phjContTable = pd.crosstab(phjTempDF[phjRiskFactorVarName],phjTempDF[phjCaseVarName])
        
        # Rearrange the order of columns so that cases come first
        # N.B. There was a bug in Pandas 0.19.2 that resulted in re-ordered dataframe columns
        # being accessed in the wrong order. This did not affect the calculation of odds ratios
        # or 95% CI. The bug was reported to Pandas GitHub on 28 Mar 2017.
        phjContTable = phjContTable[phjCaseFirst(phjTempDF = phjContTable,
                                                 phjCaseValue = phjCaseValue)]
        
        # Identify the level that represents a control value
        phjControlValue = phjContTable.columns.tolist()
        phjControlValue.remove(phjCaseValue)
        phjControlValue = phjControlValue[0]
        
        # Calcuate odds for each row
        phjContTable['odds'] = phjContTable[phjCaseValue]/phjContTable[phjControlValue]
        
        # Calculate or for each row (including baseline value – which must, by definition, equal 1)
        phjContTable['or'] = phjContTable['odds'] / phjContTable.loc[phjRiskFactorBaseValue,'odds']
        
        # Calculate 95% CI
        # ----------------
        phjRiskFactorStrata = phjTempDF[phjRiskFactorVarName].unique().tolist()
        phjRiskFactorStrata.remove(phjRiskFactorBaseValue)
        
        phjCaseControlStrata = phjTempDF[phjCaseVarName].unique().tolist()
        
        phjContTable['95pcCI_Woolf'] = "---"
        
        for phjStratum in phjRiskFactorStrata:
            # Produce a list that contains the values contained in risk factor stratum and base stratum
            # The following is a list comprehension of the form given below. It was given by Alex Martelli at:
            # http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
            # myList = [item for sublist in tempList for item in sublist]
            phjCellValuesList = [item for sublist in phjContTable.loc[[phjStratum,phjRiskFactorBaseValue],phjCaseControlStrata].values.tolist() for item in sublist]
            
            # Retrieve log OR of risk factor stratum
            phjLogOR = math.log(phjContTable.loc[phjStratum,'or'])
            
            # Calculate 1.96 x SE of natural log of odds ratio.
            # SE of log of OR is calulcated as sqrt(1/a + 1/b + 1/c + 1/d).
            phjSE_95pc = 1.96*math.sqrt(sum([1/n for n in phjCellValuesList]))
            
            # Calculate 95% CI
            phjRiskFactor95CI = ["{0:.4f}".format(round(math.exp(math.log(phjContTable.loc[phjStratum,'or']) - phjSE_95pc),2)),
                                 "{0:.4f}".format(round(math.exp(math.log(phjContTable.loc[phjStratum,'or']) + phjSE_95pc),2))]
            
            # Add list of 95pcCI to dataframe
            phjContTable.set_value(phjStratum,'95pcCI_Woolf',phjRiskFactor95CI)
            
    else:
        
        phjContTable = None
        
    return phjContTable
