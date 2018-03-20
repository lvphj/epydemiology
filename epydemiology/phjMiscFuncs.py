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


import re



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



def phjCreateNamedGroupRegex(phjTempDF,
                             phjGroupVarName,
                             phjRegexVarName,
                             phjIDVarName = None,
                             phjRegexPreCompile = False,
                             phjPrintResults = False):
    
    # Check function parameters
    # =========================
    try:
        # Check whether required parameters have been set to correct type
        assert isinstance(phjTempDF,pd.DataFrame), "Parameter, 'phjTempDF' needs to be a Pandas dataframe."
        assert isinstance(phjGroupVarName,str), "Parameter 'phjGroupVarName' needs to be a string."
        assert isinstance(phjRegexVarName,str), "Parameter 'phjRegexVarName' needs to be a string."
        
        if phjIDVarName is not None:
            assert isinstance(phjIDVarName,str), "Parameter 'phjIDVarName' (if set) needs to be a string."

        # Check whether required columns exist
        assert phjGroupVarName in phjTempDF.columns.values, "Column '{0}' is not in dataframe.".format(phjGroupVarName)
        assert phjRegexVarName in phjTempDF.columns.values, "Column '{0}' is not in dataframe.".format(phjRegexVarName)
        
        if phjIDVarName is not None:
            assert phjIDVarName in phjTempDF.columns.values, "Column '{0}' is not in dataframe.".format(phjIDVarName)
            
        # Check whether arguments are set to allowable values
        assert phjRegexPreCompile in [True, False], "Parameter 'phjRegexPreCompile' can only be True or False; it is incorrectly set."
        assert phjPrintResults in [True, False], "Parameter 'phjPrintResults' can only be True or False; it is incorrectly set."
        
    except AssertionError as e:
        print(e)
        
        phjCategoryGroupRegex = None
        
    
    # Complete function if parameter checks are OK and AssertionError not raised
    else:
        # Remove any rows where group name is empty (and reset the index)
        phjEmptyCellMask = ~(phjTempDF[phjGroupVarName] == "")
        phjTempDF = phjTempDF[phjEmptyCellMask].reset_index(drop = True)
        
        
        # Group dataframe based on phjGroupVarName and concatenate strings in phjRegexVarName, separated
        # by OR and carriage return (i.e. '|\n').
        # And sort by ID number if appropriate.
        try:
            if phjIDVarName is None:
                phjCategoryGroupRegexDF = phjTempDF.groupby(phjGroupVarName).agg({phjRegexVarName:'|'.join}).reset_index()

            else:
                phjCategoryGroupRegexDF = phjTempDF.groupby(phjGroupVarName).agg({phjRegexVarName:'|'.join,
                                                                                  phjIDVarName: 'mean'}).sort_values(phjIDVarName,
                                                                                                                     axis = 0,
                                                                                                                     ascending = True).reset_index()
                
        except pd.core.groupby.DataError as e:
            print("\nA DataError has occurred. This may occur if, for example, the '{0}' variable contains missing values. ({1}.)".format(phjIDVarName,e))
            
            phjCategoryGroupRegex = None
        
        
        # Complete function if no exception raised
        else:
            # Check that the values in the phjIDVarName variable (after the 'mean' operation) are all integers.
            # If not, if may indicate an error in the original labelling of category groups.
            phjIntegerCheckMask = phjCategoryGroupRegexDF[phjIDVarName]%1 == 0
            
            if sum(~phjIntegerCheckMask) > 0:
                if sum(~phjIntegerCheckMask) == 1:
                    print("\nWarning: there may be an error in the category ID values since one of the mean group values is not an integer.")
                else:
                    print("\nWarning: there may be an error in the category ID values since {0} mean group values are not integers.".format(sum(~phjIntegerCheckMask)))
            
            
            # Create a column containing a concatenated and combined named group regex for each group
            phjCategoryGroupRegexDF['NamedGroupRegex'] = '(?P<' + phjCategoryGroupRegexDF[phjGroupVarName].map(str).str.strip().str.replace(' ','_').str.replace('[^\w\s]','') + '>' + phjCategoryGroupRegexDF[phjRegexVarName].map(str) + ')'
            
            
            # Create a string representing entire regex
            # Various string patterns are included to ensure the final string is easier to read:
            # (?P<group1>
            #    (?:abc)|
            #    (?:cde))
            # (?P<group2>
            #    (?:fgh)|
            #    (?:ijk))
            phjCategoryGroupRegexStr = phjCategoryGroupRegexDF['NamedGroupRegex'].map(str).str.replace('>\(\?',
                                                                                                       '>\n    (?').str.replace('\)\|\(',
                                                                                                                                ')|\n    (').str.cat(others = None, sep = '|\n')
            
            if phjPrintResults == True:
                print("\nFull Regex string")
                print(phjCategoryGroupRegexStr)
            
            if phjRegexPreCompile == True:
                try:
                    phjCategoryGroupRegex = re.compile(phjCategoryGroupRegexStr,flags = re.X|re.I)

                except re.error as e:
                    print("Regex failed to compile: {0}.".format(e))
                    phjCategoryGroupRegex = None
    
    
    if phjRegexPreCompile == False:
        return phjCategoryGroupRegexStr
    else:
        return phjCategoryGroupRegex



# This function takes a column of text and uses a regex with named groups to
# determine the group to which the text best fits.
def phjFindRegexNamedGroups(phjTempDF,
                            phjDescriptorVarName,
                            phjNamedGroupRegexStr,
                            phjSeparateRegexGroups = False,
                            phjNumberMatchesVarName = 'numberMatches',
                            phjMatchedGroupVarName = 'matchedgroup',
                            phjUnclassifiedStr = 'unclassified',
                            phjMultipleMatchStr = 'multiple',
                            phjCleanup = False,
                            phjPrintResults = False):
    
    
    # Check function parameters are set correctly
    try:
        # Check whether required parameters have been set to correct type
        assert isinstance(phjTempDF,pd.DataFrame), "Parameter, 'phjTempDF' needs to be a Pandas dataframe."
        assert isinstance(phjDescriptorVarName,str), "Parameter 'phjDescriptorVarName' needs to be a string."
        assert isinstance(phjNamedGroupRegexStr,str), "Parameter 'phjNamedGroupRegexStr' needs to be a string. The function does not accept a pre-compiled regular expression."
        assert isinstance(phjNumberMatchesVarName,str), "Parameter 'phjNumberMatchesVarName' needs to be a string."
        assert isinstance(phjMatchedGroupVarName,str), "Parameter 'phjMatchedGroupVarName' needs to be a string."
        assert isinstance(phjUnclassifiedStr,str), "Parameter 'phjUnclassifiedStr' needs to be a string."
        assert isinstance(phjMultipleMatchStr,str), "Parameter 'phjMultipleMatchStr' needs to be a string."
        
        # Check whether arguments are set to allowable values
        assert phjSeparateRegexGroups in [True, False], "Parameter 'phjSeparateRegexGroups' can only be True or False; it is incorrectly set."
        assert phjCleanup in [True, False], "Parameter 'phjCleanup' can only be True or False; it is incorrectly set."
        assert phjPrintResults in [True, False], "Parameter 'phjPrintResults' can only be True or False; it is incorrectly set."
        
        # Check that referenced columns exist in the dataframe
        assert phjDescriptorVarName in phjTempDF.columns, "The column '{0}' does not exist in the dataframe.".format(phjDescriptorVarName)
        
        # Check that new column names do not already exist
        assert phjNumberMatchesVarName not in phjTempDF.columns, "The column name '{0}' already exists.".format(phjNumberMatchesVarName)
        assert phjMatchedGroupVarName not in phjTempDF.columns, "The column name '{0}' already exists.".format(phjMatchedGroupVarName)
        
    except AssertionError as e:
        print("An AssertionError occurred. ({0})".format(e))
    
    else:
        try:
            # Try to compile the full and complete named-group regex containing
            # multiple named groups.
            phjNamedGroupRegex = re.compile(phjNamedGroupRegexStr,flags = re.I|re.X)
        
        except re.error as e:
            print("Regex failed to compile: {0}.".format(e))
        
        # Continue with function if regex compiles
        else:
            # Run the named-group regex as a single regex. (This may result in some matches being missed
            # if preceding mathces are found because grouped regexes cannot overlap.)
            if phjSeparateRegexGroups == False:
                # Create a dataframe with a column for each named group in the regex
                phjScratchDF = phjTempDF[phjDescriptorVarName].str.extract(phjNamedGroupRegex, expand = True)
                
                # Add the descriptor column only from the original dataframe
                phjScratchDF = phjScratchDF.join(phjTempDF[phjDescriptorVarName])
                
                # Move descriptor column to the front
                cols = phjScratchDF.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                phjScratchDF = phjScratchDF[cols]
            
            # Run each named group regex separately to ensure all group matches are identified.
            # It is more likely that multiple group matches may be identified.
            else:
                # Create dataframe containing matched species.
                # This routine is based on a function supplied by Nathan Vērzemnieks on 19 Feb 2018
                # on StackOverflow in response to a question.
                # https://stackoverflow.com/questions/48858357/extract-named-group-regex-pattern-from-a-compiled-regex-in-python
                # Nathan Vērzemnieks said:
                # The argument to re.split looks for a literal pipe [and white space] followed by [a non-capturing look-ahead for]
                # the (?=< , the beginning of a named group. It compiles each subpattern and uses the groupindex attribute to
                # extract the name.
                phjScratchDF = phjTempDF.loc[:,[phjDescriptorVarName]]
                
                for subpattern in re.split('\|\s*(?=\(\?P<)', phjNamedGroupRegexStr):
                    phjGroupRegex = re.compile(subpattern,flags = re.I|re.X)
                    phjGroupName = list(phjGroupRegex.groupindex)[0]
                    
                    phjScratchDF[phjGroupName] = phjScratchDF[phjDescriptorVarName].str.extract(phjGroupRegex,
                                                                                                expand = False)
                    
                    if phjPrintResults == True:
                        print(phjGroupName + ' ... done')
                    else:
                        print('.',end = '')
                        
                print("\n")
            
            # Create a new column that contains a count of the number of matches.
            # Obviously, it should only be 1 but it is possible that a small number of cases
            # may have more than 1 match.
            # Some cases may not be classified.
            phjGroupNamesList = list(phjNamedGroupRegex.groupindex)
            phjScratchDF[phjNumberMatchesVarName] = phjScratchDF[phjGroupNamesList].count(axis = 1)
            
            if phjPrintResults == True:
                # Frequency table showing number of group matches
                print("\nTable of number of group matches identified per description term\n")
                print(pd.DataFrame(phjScratchDF[phjNumberMatchesVarName].value_counts(sort = False)).rename_axis('Number of matches').rename(columns = {phjNumberMatchesVarName:'Frequency'}))
                print("\n")
            
            # Create a new column that contains the name of the matched group for rows where a regex match was identified
            phjScratchDF[phjMatchedGroupVarName] = np.nan
            
            for grp in phjGroupNamesList:
                phjScratchDF.loc[(phjScratchDF[grp].notnull()) & (phjScratchDF[phjNumberMatchesVarName] == 1),phjMatchedGroupVarName] = grp
            
            # Replace rows with no match to unclassified
            phjScratchDF.loc[phjScratchDF[phjNumberMatchesVarName] == 0,phjMatchedGroupVarName] = phjUnclassifiedStr
            
            # Replace rows with multiple matches to multiple match string
            phjScratchDF.loc[phjScratchDF[phjNumberMatchesVarName] > 1,phjMatchedGroupVarName] = phjMultipleMatchStr
            
            if phjCleanup == False:
                # Check that none of the regex group names already exist as column headings in
                # the original dataframe
                for grp in phjGroupNamesList:
                    if grp in phjTempDF.columns.values:
                        print("One or more group names in the regular expression clash with column headings in the dataframe. In order to avoid confusion, the phjCleanup variable has been set to True.")
                        phjCleanup = True
            
            # Remove the temporary columns before joining with original dataframe.
            if phjCleanup == True:
                phjScratchDF = phjScratchDF.drop(phjGroupNamesList,
                                                 axis = 1)
            
            # Join phjScratchDF to original database
            phjTempDF = phjTempDF.join(phjScratchDF.loc[:,phjScratchDF.columns != phjDescriptorVarName],
                                       how = 'left')

            if phjPrintResults == True:
                # Print samples of rows of dataframe
                with pd.option_context('display.max_rows', 20, 'display.max_columns', 20):
                    print(phjTempDF)
    
    return phjTempDF



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
        phjTempDF[phjNewColName] = phjTempDF.columns[phjTempDF.columns.get_loc(phjLastCol) - phjTempDF['posFromR'] + 1]
        
        # If the posFromR value is greater than the number of columns listed then the row of cells
        # must have consisted of all zeroes. Therefore, replace all such occurrences with some
        # indicator e.g. 'unclassified'.
        nCols = phjTempDF.columns.get_loc(phjLastCol) - phjTempDF.columns.get_loc(phjFirstCol) + 1
        phjMask = phjTempDF['posFromR'].astype(int) > nCols
        phjTempDF.loc[phjMask,phjNewColName] = 'unclassified'
        
        # Remove temporary columns
        if phjCleanup == True:
            phjTempDF = phjTempDF.drop(['bin','posFromR'],
                                       axis = 1)
        
        # Print dataframe
        if phjPrintResults == True:
            print(phjTempDF)
    
    else:
        phjTempDF = phjTempDF
        
    return phjTempDF



if __name__ == '__main__':
    main()

