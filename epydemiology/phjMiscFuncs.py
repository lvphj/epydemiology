import pkg_resources

try:
    pkg_resources.get_distribution('numpy')
except pkg_resources.DistributionNotFound:
    numpyPresent = False
    print("Error: Numpy package not available.")
else:
    numpyPresent = True
    import numpy as np


try:
    pkg_resources.get_distribution('pandas')
except pkg_resources.DistributionNotFound:
    pandasPresent = False
    print("Error: Pandas package not available.")
else:
    pandasPresent = True
    import pandas as pd


import collections



def phjGetStrFromArgOrFile(phjStr = None,
                           phjPathAndFileName = None,
                           phjAllowedAttempts = 3,
                           phjPrintResults = False):
    
    # This function retrieves a string either from a string contained in a text file
    # given by a path and file name, or from a string entered as an argument for this
    # function. A string saved in a file is given preference (i.e. this is checked first).
    
    # Initially set phjTempStr to be None
    phjTempStr = None
    
    # If one or other of the string input options is not None then get query string
    if (phjStr is not None) or (phjPathAndFileName is not None):
        # File name and path given preference (i.e. check this first)
        if phjPathAndFileName is not None:
            # Load SQL query from text file
            phjTempStr = phjReadTextFromFile(phjFilePathAndName = phjPathAndFileName,
                                             phjMaxAttempts = phjAllowedAttempts,
                                             phjPrintResults = phjPrintResults)
            
            if phjPrintResults == True:
                print("\nString retrieved from file ('{0}'):".format(phjPathAndFileName))
                print(phjTempStr)
        
        # If the text file did not yield a string, move on to the query string.
        if (phjTempStr is None) and (phjStr is not None):
            phjTempStr = phjStr
            
            if phjPrintResults == True:
                print("\nString retrieved from passed argument (phjStr):")
                print(phjTempStr)
    
    else:
        phjTempStr = None
    
    return phjTempStr



def phjReadTextFromFile(phjFilePathAndName = None,
                        phjMaxAttempts = 3,
                        phjPrintResults = False):
    
    for i in range(phjMaxAttempts):
        
        if (phjFilePathAndName is None) or (i > 0):
            phjFilePathAndName = input('Enter path and filename for file containing text (e.g. query or regex): ')
        
        try:
            # The following original code ran the risk of not closing the file if a
            # problem occurred.
            # phjTempFileObject = open(phjFilePathAndName)
            # phjTempText = phjTempFileObject.read()
            # phjTempFileObject.close()
            
            with open(phjFilePathAndName,'r') as phjTempFileObject:
                phjTempText = phjTempFileObject.read()
            
            if phjPrintResults:
                print('Text read from file:')
                print(phjTempText)
                print('\n')
            
            break
        
        except FileNotFoundError as e:
            
            print("\nA FileNotFoundError occurred.\nError number {0}: {1}. File named \'{2}\' does not exist at that location.".format(e.args[0],e.args[1],phjFilePathAndName))
            
            if i < (phjMaxAttempts-1):
                print('\nPlease re-enter path and filename details.\n')    # Only say 'Please try again' if not last attempt.
            
            else:
                # If file can't be found then set phjTempText to None
                print('\nFailed to find file containing text after {0} attempts.\n'.format(i+1))
                phjTempText = None
    
    return phjTempText



def phjMaxLevelOfTaxonomicDetail(phjTempDF,
                                 phjFirstCol,
                                 phjLastCol,
                                 phjNewColName = 'newColumn',
                                 phjDropPreExisting = False,
                                 phjCleanup = False,
                                 phjPrintResults = False):
    
    # Check function parameters have been set to reasonable values
    try:
        # Check whether required parameters have been set to correct type
        assert isinstance(phjTempDF,pd.DataFrame), "Parameter 'phjTempDF' needs to be a Pandas dataframe."
        assert isinstance(phjFirstCol,str), "Argument 'phjFirstCol' needs to be a string."   # In Python 2, use isinstance(s,basestring)
        assert isinstance(phjLastCol,str), "Argument 'phjLastCol' needs to be a string."
        assert isinstance(phjNewColName,str), "Argument 'phjNewColName' needs to be a string."
        
        # Check whether required columns exist
        assert phjFirstCol in phjTempDF.columns.values, "Column '{0}' is not in dataframe.".format(phjFirstCol)
        assert phjLastCol in phjTempDF.columns.values, "Column '{0}' is not in dataframe.".format(phjLastCol)
        assert phjTempDF.columns.get_loc(phjLastCol) - phjTempDF.columns.get_loc(phjFirstCol) > 0, "Columns are given in the wrong order; '{0}' (phjFirstCol) needs to occur BEFORE '{1}' (phjLastCol) in the dataframe.".format(phjFirstCol,phjLastCol)
        
        # Check whether arguments are set to allowable values
        assert phjDropPreExisting in [True,False], "Argument 'phjDropPreExisting' can only be True or False; it is incorrectly set."
        assert phjCleanup in [True,False], "Argument 'phjCleanup' can only be True or False; it is incorrectly set."
        assert phjPrintResults in [True,False], "Argument 'phjPrintResults' can only be True or False; it is incorrectly set."
        
        # Check whether columns that will be created already exist
        if phjDropPreExisting == False:
            assert 'bin' not in phjTempDF.columns.values, "A column named 'bin' will be temporarily created but already exists; please rename."
            assert 'posFromR' not in phjTempDF.columns.values, "A column named 'posFromR' will be temporarily created but already exists; please rename."
            assert phjNewColName not in phjTempDF.columns.values, "A column named '{0}' (phjNewColName) will be permanently created but already exists; please choose a different name.".format(phjNewColName)
        
        phjCheckPassed = True
    
    
    except AssertionError as e:
        print(e)
        
        phjCheckPassed = False
    
    
    
    if phjCheckPassed == True:
        
        # If columns already exist, drop from dataframe
        if phjDropPreExisting == True:
            if 'bin' in phjTempDF.columns.values:
                phjTempDF = phjTempDF.drop('bin',axis = 1)

            if 'posFromR' in phjTempDF.columns.values:
                phjTempDF = phjTempDF.drop('posFromR',axis = 1)

            if 'bin' in phjTempDF.columns.values:
                phjTempDF = phjTempDF.drop('bin',axis = 1)
        
        
        # A discussion of solutions to convert a dataframe with strings and empty cells to binary is given at:
        # https://stackoverflow.com/questions/49003150/creating-a-binary-representation-of-whether-a-string-is-present-or-not-in-a-pand
        # Several options given.
        # Decided to use a Pandas-based option suggested by jezrael (although Numpy options may be quicker)
        phjRangeOfCols = list(range(phjTempDF.columns.get_loc(phjFirstCol),
                                    phjTempDF.columns.get_loc(phjLastCol) + 1))
        
        phjTempDF['bin'] = (phjTempDF.iloc[:,phjRangeOfCols] != '').astype(int).astype(str).values.sum(axis=1)
        
        # Number of digits from right
        # ---------------------------
        # This method makes use of the idea of two's-complement
        #(see https://en.wikipedia.org/wiki/Two%27s_complement#From_the_ones'_complement).
        # The algorithm to find the position of the rightmost set bit (i.e. the position
        # on the right that is set to '1') is given at:
        # https://www.geeksforgeeks.org/position-of-rightmost-set-bit/
        
        # The algorithm is described as:
        # Algorithm: (Example 18(010010))
        # Let I/P be 12 (1100)
        #
        # 1. Take two's complement of the given no as all bits are reverted
        # except the first '1' from right to left (10111)
        # 
        # 2  Do an bit-wise & with original no, this will return no with the
        # required one only (00010)
        # 
        # 3  Take the log2 of the no, you will get position -1 (1)
        # 
        # 4  Add 1 (2)
        
        # The site also gave the following Python code:
        # Python Code for Position
        # of rightmost set bit
        # 
        # import math
        # 
        # def getFirstSetBitPos(n):
        #  
        #     return math.log2(n&-n)+1
        #
        # # driver code
        #
        # n = 12
        # print(int(getFirstSetBitPos(n)))
        # 
        # This code is contributed
        # by Anant Agarwal.
        
        # This was adapted to use array arithmatic in a Pandas dataframe:
        # df['pos'] = (np.log2(df['bin']&-df['bin'])+1).astype(int)
        
        # Position of rightmost set bit
        #phjTempDF['posFromR'] = (np.log2(phjTempDF['bin'].astype(int) & -phjTempDF['bin'].astype(int)) + 1).astype(int)
        
        
        # If all cells in a row were empty, the binary representation would be 000...000. This causes
        # big problems when trying to calculate the two's complement because log2(0) is infinity.
        # To overcome this problem, add a '1' to start of each string; this won't affect the calculation
        # of the rightmost set bit except in cases where all cells are empty, in which case the rightmost
        # set bit will lie outside the number of columns being considered.
        phjTempDF['posFromR'] = (np.log2( ('1' + phjTempDF['bin']).astype(int) & -('1' + phjTempDF['bin']).astype(int)) + 1).astype(int)
        
        # Count back from the last column to find the column containing the last string entry
        phjTempDF[phjNewColName] = phjTempDF.columns[phjTempDF.columns.get_loc(phjLastCol) - df['posFromR'] + 1]
        
        # If the posFromR value is greater than the number of columns listed then the row of cells
        # must have consisted of all zeroes. Therefore, replace all such occurrences with some
        # indicator e.g. 'unclassified'.
        nCols = phjTempDF.columns.get_loc(phjLastCol) - phjTempDF.columns.get_loc(phjFirstCol) + 1
        phjMask = phjTempDF['posFromR'].astype(int) > nCols
        phjTempDF.loc[phjMask,phjNewColName] = 'unclassified'
        
        # Remove temporary columns
        if phjCleanup == True:
            phjTempDF = df.drop(['bin','posFromR'],
                                 axis = 1)
        
        # Print dataframe
        if phjPrintResults == True:
            print(phjTempDF)
    
    else:
        phjTempDF = phjTempDF
        
    return phjTempDF



if __name__ == '__main__':
    main()

