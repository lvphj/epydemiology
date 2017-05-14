def phjBinaryVarsToSquareMatrix(phjDataDF,
                                phjColumnNamesList,
                                phjOutputFormat = 'arr',
                                phjPrintResults = False):
    
    try:
        phjTempDF = phjDataDF[phjColumnNamesList]
        
    except KeyError as e:
        print('A KeyError has occurred ({0}). Check that the column names provided exist in the dataframe.'.format(e))
        return None
    
    phjTempDF['rowSum'] = phjTempDF[phjColumnNamesList].sum(axis=1)

    # Create a blank square matrix (in dataframe form) with column and row indices the same
    phjTempMatrixDF = pd.DataFrame(columns=phjColumnNamesList,index=phjColumnNamesList)

    # Start by completing the diagonal
    # ================================
    # Use just those rows with only a single entry (i.e. only one variable is entered).
    # Create a series containing the name of the variable and the sum of entries
    phTempSer = phjTempDF.loc[phjTempDF['rowSum']==1,phjColumnNamesList].sum(axis=0)
    
    # Step through each diagonal cell in the matrix and enter tbe sum value
    for c in phjColumnNamesList:
        phjTempMatrixDF.loc[c,c]=phTempSer[c]

    # Next fill in the rest of the matrix
    # ===================================
    # Step through each variable in the list and create a series consisting
    # of all OTHER variables and the number of entries or those variables
    for c in phjColumnNamesList:
        phjOtherCols = [i for i in columns if i!=c]
        phjTempSer = phjTempDF.loc[(phjTempDF['rowSum']>1) & (phjTempDF[c]==1),phjOtherCols].sum(axis=0)
        
        # For each row index, step through each column and add the data
        for oc in phjOtherCols:
            phjTempMatrixDF.loc[c,oc] = phjTempSer[oc]
	
	if phjPrintResults == True:
		print(phjTempMatrixDF)
		
    if phjOutputFormat == 'arr':
    	return phjTempMatrixDF.values
    	
    elif phjOutputFormat == 'df':
    	return phjTempMatrixDF
    	
    else:
    	print('The phjOutputFormat parammeter was set to an unknown value (\'{0}\'). The return value was set to None.'.format(phjOutputFormat))
    	return None
    	