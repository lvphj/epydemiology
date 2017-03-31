import numpy as np
import pandas as pd
import math


def phjOddsRatio(phjTempDF,
                 phjCaseVarName,
                 phjCaseValue,
                 phjRiskFactorVarName,
                 phjRiskFactorBaseValue):
    
    # Check passed parameters are useable
    phjCheckPassed = phjCheckVars(phjTempDF = phjTempDF,
                                  phjCaseVarName = phjCaseVarName,
                                  phjCaseValue = phjCaseValue,
                                  phjRiskFactorVarName = phjRiskFactorVarName,
                                  phjRiskFactorBaseValue = phjRiskFactorBaseValue)
    
    # Data to use - remove rows that have a missing value
    phjTempDF = phjRemoveNaNRows(phjTempDF = phjTempDF,
                                 phjCaseVarName = phjCaseVarName,
                                 phjRiskFactorVarName = phjRiskFactorVarName)
    
    if phjCheckPassed:
        
        # Create a basic 2 x 2 (or n x 2) contingency table
        phjContTable = phjCreateContingencyTable(phjTempDF = phjTempDF,
                                                 phjCaseVarName = phjCaseVarName,
                                                 phjCaseValue = phjCaseValue,
                                                 phjRiskFactorVarName = phjRiskFactorVarName,
                                                 phjRiskFactorBaseValue = phjRiskFactorBaseValue)
        
        
        # Identify the code that represents a control value
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
            
            # Calculate 1.96 x SE of natural log of odds ratio.
            # SE of log of OR is calulcated as sqrt(1/a + 1/b + 1/c + 1/d).
            phjSE = math.sqrt(sum([1/n for n in phjCellValuesList]))
            
            # Calculate 95% CI
            phjRiskFactorCI = phjCalcCI_lognormal(phjUntransformedPointEstimate = phjContTable.loc[phjStratum,'or'],
                                                  phjTransformedSE = phjSE)
            
            # Add list of 95pcCI to dataframe
            phjContTable.set_value(phjStratum,'95pcCI_Woolf',phjRiskFactorCI)
            
    else:
        
        phjContTable = None
        
    return phjContTable



def phjRelativeRisk(phjTempDF,
                    phjCaseVarName,
                    phjCaseValue,
                    phjRiskFactorVarName,
                    phjRiskFactorBaseValue):

    # Check passed parameters are useable
    phjCheckPassed = phjCheckVars(phjTempDF = phjTempDF,
                                  phjCaseVarName = phjCaseVarName,
                                  phjCaseValue = phjCaseValue,
                                  phjRiskFactorVarName = phjRiskFactorVarName,
                                  phjRiskFactorBaseValue = phjRiskFactorBaseValue)
    
    # Data to use - remove rows that have a missing value
    phjTempDF = phjRemoveNaNRows(phjTempDF = phjTempDF,
                                 phjCaseVarName = phjCaseVarName,
                                 phjRiskFactorVarName = phjRiskFactorVarName)
    
    if phjCheckPassed:
        
        # Create a basic 2 x 2 (or n x 2) contingency table
        phjContTable = phjCreateContingencyTable(phjTempDF =  phjTempDF,
                                                 phjCaseVarName = phjCaseVarName,
                                                 phjCaseValue = phjCaseValue,
                                                 phjRiskFactorVarName = phjRiskFactorVarName,
                                                 phjRiskFactorBaseValue = phjRiskFactorBaseValue)
        
        
        # Identify the level that represents a control value
        phjControlValue = phjContTable.columns.tolist()
        phjControlValue.remove(phjCaseValue)
        phjControlValue = phjControlValue[0]
        
        # Calcuate risk for each row
        phjContTable['risk'] = phjContTable[phjCaseValue]/(phjContTable[phjCaseValue] + phjContTable[phjControlValue])
        
        # Calculate rr for each row (including baseline value – which must, by definition, equal 1)
        phjContTable['rr'] = phjContTable['risk'] / phjContTable.loc[phjRiskFactorBaseValue,'risk']
        
        # Calculate 95% CI
        # ----------------
        phjRiskFactorStrata = phjTempDF[phjRiskFactorVarName].unique().tolist()
        phjRiskFactorStrata.remove(phjRiskFactorBaseValue)
        
        phjCaseControlStrata = phjTempDF[phjCaseVarName].unique().tolist()
        
        phjContTable['95pcCI'] = "---"
        
        for phjStratum in phjRiskFactorStrata:
            # The values in the cells that represent a, b, c, and d can be stored in a list (as
            # with the odds ratio calculation because there is a bug in Pandas 0.19.2 that resulted
            # in the order of cells being retrieveed in the wrong order. This bug was reported.
            # Instead, retrieve vaclues from table and allocate to variables nameed a, b, c, d and
            # then stor in a list
            a = phjContTable.loc[phjStratum,phjCaseValue]
            b = phjContTable.loc[phjStratum,phjControlValue]
            c = phjContTable.loc[phjRiskFactorBaseValue,phjCaseValue]
            d = phjContTable.loc[phjRiskFactorBaseValue,phjControlValue]
            
            phjCellValuesDict = {}
            phjCellValuesDict['a'] = a
            phjCellValuesDict['b'] = b
            phjCellValuesDict['c'] = c
            phjCellValuesDict['d'] = d
            
            # Calculate SE of natural log of relative risk.
            # SE of log of RR is calulcated as sqrt( b/(a(a+b)) + d/(c(c+d)) ).
            phjSE = math.sqrt( ( phjCellValuesDict['b'] / ( phjCellValuesDict['a']*( phjCellValuesDict['a'] + phjCellValuesDict['b'] ) ) ) +
                               ( phjCellValuesDict['d'] / ( phjCellValuesDict['c']*( phjCellValuesDict['c'] + phjCellValuesDict['d'] ) ) ) )
            
            # Calculate 95% CI
            phjRiskFactorCI = phjCalcCI_lognormal(phjUntransformedPointEstimate = phjContTable.loc[phjStratum,'rr'],
                                                  phjTransformedSE = phjSE)
            
            # Add list of 95pcCI to dataframe
            phjContTable.set_value(phjStratum,'95pcCI',phjRiskFactorCI)
            
    else:
        
        phjContTable = None
                    
    return phjContTable



def phjCheckVars(phjTempDF,
                 phjCaseVarName,
                 phjCaseValue,
                 phjRiskFactorVarName,
                 phjRiskFactorBaseValue):
    
    # Check cases variable occurs and there are only 2 categories
    phjCheckPassed = phjCaseVarCheck(phjTempDF = phjTempDF,
                                     phjCaseVarName = phjCaseVarName)
    
    # Check values occur in variables.
    # BUT only need to do this if phjCheckPassed is True. If if is False then do not
    # change it back to True.
    if phjCheckPassed == True:
        for i,j in [[phjCaseValue,phjCaseVarName],[phjRiskFactorBaseValue,phjRiskFactorVarName]]:
            if phjCheckPassed == True:
                phjCheckPassed = phjValueCheck(phjTempDF = phjTempDF,
                                               phjVarName = j,
                                               phjValue = i)
    
    return phjCheckPassed



def phjCaseVarCheck(phjTempDF,
                    phjCaseVarName):
    
    # This function checks the following:
    # i.  The name passed to the function giving the case variable actually exists in the dataframe
    # ii. The case variable contains only 2 levels
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



def phjValueCheck(phjTempDF,
                  phjVarName,
                  phjValue):
    
    # This function check that values passed to the function actually exist in the variable where they are supposed to occur,
    # e.g. if a case is identified with 'y', make sure that 'y' occurs in the case variable.
    try:
        assert phjValue in phjTempDF[phjVarName].unique(),'The value {0} does not exist in variable {1}.'.format(phjValue,phjVarName)
        phjCheckPassed = True
        
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
    
    

def phjRemoveNaNRows(phjTempDF,
                     phjCaseVarName,
                     phjRiskFactorVarName):
    
    phjTempDF = phjTempDF[[phjCaseVarName,phjRiskFactorVarName]].dropna(axis = 0, how = 'any').reset_index(drop = True)
    
    return phjTempDF



def phjCreateContingencyTable(phjTempDF,
                              phjCaseVarName,
                              phjCaseValue,
                              phjRiskFactorVarName,
                              phjRiskFactorBaseValue):

        # Calculated univariable contingency table with risk factor levels as index and
        # cases and controls as columns.
        phjContTable = pd.crosstab(phjTempDF[phjRiskFactorVarName],phjTempDF[phjCaseVarName])
        
        # Rearrange the order of columns so that cases come first
        # N.B. There was a bug in Pandas 0.19.2 that resulted in re-ordered dataframe columns
        # being accessed in the wrong order. This did not affect the calculation of odds ratios
        # or 95% CI. The bug was reported to Pandas GitHub on 28 Mar 2017.
        phjContTable = phjContTable[phjCaseFirst(phjTempDF = phjContTable,
                                                 phjCaseValue = phjCaseValue)]

        return phjContTable



def phjCalcCI_lognormal (phjUntransformedPointEstimate,
                         phjTransformedSE):
    # This function takes an UNTRANSFORMED, log-normally distributed point estimate (e.g. either RR or OR) together with SE of
    # the LOG-TRANSFORMED point estimate and returns a list containing the lower and upper limits of the confidence interval,
    # back-transformed to the origianl scale.
    phjLowerLimit = "{0:.4f}".format(round(math.exp(math.log(phjUntransformedPointEstimate) - 1.96*phjTransformedSE),4))
    phjUpperLimit = "{0:.4f}".format(round(math.exp(math.log(phjUntransformedPointEstimate) + 1.96*phjTransformedSE),4))
    
    return [phjLowerLimit, phjUpperLimit]
