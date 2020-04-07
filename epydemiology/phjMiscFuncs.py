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
import collections
import inspect

from .phjTestFunctionParameters import phjAssert



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
            phjTempStr = phjReadTextFromFile(phjPathAndFileName = phjPathAndFileName,
                                             phjMaxAttempts = phjAllowedAttempts,
                                             phjPrintResults = False)
            
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



def phjReadTextFromFile(phjPathAndFileName = None,
                        phjMaxAttempts = 3,
                        phjPrintResults = False):
    
    for i in range(phjMaxAttempts):
        
        if (phjPathAndFileName is None) or (i > 0):
            phjPathAndFileName = input('Enter path and filename for file containing text (e.g. query or regex): ')
        
        try:
            # The following original code ran the risk of not closing the file if a
            # problem occurred.
            # phjTempFileObject = open(phjFilePathAndName)
            # phjTempText = phjTempFileObject.read()
            # phjTempFileObject.close()
            
            with open(phjPathAndFileName,'r') as phjTempFileObject:
                phjTempText = phjTempFileObject.read()
            
            if phjPrintResults:
                print('Text read from file:')
                print(phjTempText)
                print('\n')
            
            break
        
        except FileNotFoundError as e:
            
            print("\nA FileNotFoundError occurred.\nError number {0}: {1}. File named \'{2}\' does not exist at that location.".format(e.args[0],e.args[1],phjPathAndFileName))
            
            if i < (phjMaxAttempts-1):
                print('\nPlease re-enter path and filename details.\n')    # Only say 'Please try again' if not last attempt.
            
            else:
                # If file can't be found then set phjTempText to None
                print('\nFailed to find file containing text after {0} attempts.\n'.format(i+1))
                phjTempText = None
    
    return phjTempText



def phjCreateNamedGroupRegex(phjDF,
                             phjGroupVarName,
                             phjRegexVarName,
                             phjIDVarName = None,
                             phjRegexPreCompile = False,
                             phjPrintResults = False):
    
    # Check function parameters
    # =========================
    try:
        # Check whether required parameters have been set to correct type
        assert isinstance(phjDF,pd.DataFrame), "Parameter, 'phjDF' needs to be a Pandas dataframe."
        assert isinstance(phjGroupVarName,str), "Parameter 'phjGroupVarName' needs to be a string."
        assert isinstance(phjRegexVarName,str), "Parameter 'phjRegexVarName' needs to be a string."
        
        if phjIDVarName is not None:
            assert isinstance(phjIDVarName,str), "Parameter 'phjIDVarName' (if set) needs to be a string."

        # Check whether required columns exist
        assert phjGroupVarName in phjDF.columns.values, "Column '{0}' is not in dataframe.".format(phjGroupVarName)
        assert phjRegexVarName in phjDF.columns.values, "Column '{0}' is not in dataframe.".format(phjRegexVarName)
        
        if phjIDVarName is not None:
            assert phjIDVarName in phjDF.columns.values, "Column '{0}' is not in dataframe.".format(phjIDVarName)
            
        # Check whether arguments are set to allowable values
        assert phjRegexPreCompile in [True, False], "Parameter 'phjRegexPreCompile' can only be True or False; it is incorrectly set."
        assert phjPrintResults in [True, False], "Parameter 'phjPrintResults' can only be True or False; it is incorrectly set."
        
        # Check whether there are named groups contained in the regexes; the named group
        # format is created based on the phjGroupVarName variable and, therefore, the
        # individual regex components should not contain a named group. The regex looks
        # for the pattern (?P<...>
        assert phjDF[phjRegexVarName].str.match('\(\?P<\w+>').sum() == 0, "Regexes should not contain a named group."
        
        # Check whether there are capture groups contained in the regexes. The regexes
        # are not intended to capture text but rather to determine whether regex matches
        # are present. This regex checks for a round bracket that is NOT followed by a
        # question mark plus some other characters followed by a closing round bracket.
        # The regex looks for set of round brackets where the opening brackets is not
        # followed by question mark.
        assert phjDF[phjRegexVarName].str.match('\((?!\?).+?\)').sum() == 0, "Regexes should not contain capture groups."
        
    except AssertionError as e:
        # Set return value to none
        phjCategoryGroupRegex = None
        
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
            raise
        
    # Complete function if parameter checks are OK and AssertionError not raised
    # ==========================================================================
    else:
        # Remove any rows where group name is empty (and reset the index)
        phjEmptyCellMask = ~(phjDF[phjGroupVarName] == "")
        phjDF = phjDF[phjEmptyCellMask].reset_index(drop = True)
        
        
        # Group dataframe based on phjGroupVarName and concatenate strings in phjRegexVarName, separated
        # by OR and carriage return (i.e. '|\n').
        # And sort by ID number if appropriate.
        try:
            if phjIDVarName is None:
                phjCategoryGroupRegexDF = phjDF.groupby(phjGroupVarName).agg({phjRegexVarName:'|'.join}).reset_index()
            
            else:
                phjCategoryGroupRegexDF = phjDF.groupby(phjGroupVarName).agg({phjRegexVarName:'|'.join,
                                                                                  phjIDVarName: 'mean'}).sort_values(phjIDVarName,
                                                                                                                     axis = 0,
                                                                                                                     ascending = True).reset_index()
                
                # Check that the values in the phjIDVarName variable (after the 'mean' operation) are all integers.
                # If not, itq may indicate an error in the original labelling of category groups.
                phjIntegerCheckMask = phjCategoryGroupRegexDF[phjIDVarName]%1 == 0
            
                if sum(~phjIntegerCheckMask) > 0:
                    if sum(~phjIntegerCheckMask) == 1:
                        print("\nWarning: there may be an error in the category ID values since one of the mean group values is not an integer.")
                    else:
                        print("\nWarning: there may be an error in the category ID values since {0} mean group values are not integers.".format(sum(~phjIntegerCheckMask)))
        
        except pd.core.groupby.DataError as e:
            if inspect.stack()[1][3] == '<module>':
                print("\nA DataError has occurred in {fname}() function. This may occur if, for example, the '{var}' variable contains missing values. ({msg})\n".format(msg = e,
                                                                                                                                                                          fname = inspect.stack()[0][3],
                                                                                                                                                                          var = phjIDVarName))
            else:
                # If function has been called by another function then modify message and re-raise exception
                print("\nA DataError has occurred in {fname}() function when called by {callfname}() function. This may occur if, for example, the '{var}' variable contains missing values. ({msg})\n".format(msg = e,
                                                                                                                                                                                                               fname = inspect.stack()[0][3],
                                                                                                                                                                                                               var = phjIDVarName,
                                                                                                                                                                                                               callfname = inspect.stack()[1][3]))
                raise
            
            phjCategoryGroupRegex = None
        
        # Complete function if no exception raised
        else:
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
                    if inspect.stack()[1][3] == '<module>':
                        print("Regex failed to compile in {fname}() function: {msg}.".format(msg = e,
                                                                                             fname = inspect.stack()[0][3]))
                    else:
                        # If function has been called by another function then modify message and re-raise exception
                        print("Regex failed to compile in {fname}() function when called by {callfname}() function: {msg}.".format(msg = e,
                                                                                                                                   fname = inspect.stack()[0][3],
                                                                                                                                   callfname = inspect.stack()[1][3]))
                        raise
                        
                    phjCategoryGroupRegex = None
            
            else:
                # In the regex has not been compiled then return the string
                return phjCategoryGroupRegexStr
    
    return phjCategoryGroupRegex



# This function takes a column of text and uses a regex with named groups to
# determine the group to which the text best fits.
def phjFindRegexNamedGroups(phjDF,
                            phjDescriptorVarName,
                            phjNamedGroupRegexStr,
                            phjSeparateRegexGroups = False,
                            phjNumberMatchesVarName = 'numberMatches',
                            phjMatchedGroupVarName = 'matchedgroup',
                            phjUnclassifiedStr = 'unclassified',
                            phjMultipleMatchStr = 'multiple',
                            phjCleanup = False,
                            phjPrintResults = False):
    
    
    # Check whether required parameters have been set to correct type and are
    # set to allowable values
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjDescriptorVarName',phjDescriptorVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        phjAssert('phjNamedGroupRegexStr',phjNamedGroupRegexStr,str)
        phjAssert('phjSeparateRegexGroups',phjSeparateRegexGroups,bool)
        phjAssert('phjNumberMatchesVarName',phjNumberMatchesVarName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjMatchedGroupVarName',phjMatchedGroupVarName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjUnclassifiedStr',phjUnclassifiedStr,str)
        phjAssert('phjMultipleMatchStr',phjMultipleMatchStr,str)
        phjAssert('phjCleanup',phjCleanup,bool)
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
        # Could also check that each named group does not already exist as a column name.
        # Actually this is done when the phjScratchDF is joined back to the original
        # dataframe (see below).
        
        
    except AssertionError as e:
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})".format(msg = e,
                                                                                     fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})".format(msg = e,
                                                                                                                           fname = inspect.stack()[0][3],
                                                                                                                           callfname = inspect.stack()[1][3]))
            raise
    
    else:
        try:
            # Try to compile the full and complete named-group regex containing
            # multiple named groups.
            phjNamedGroupRegex = re.compile(phjNamedGroupRegexStr,flags = re.I|re.X)
        
        except re.error as e:
            if inspect.stack()[1][3] == '<module>':
                print("Regex failed to compile in {fname}() function: {msg}\n.".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
            else:
                # If function has been called by another function then modify message and re-raise exception
                print("Regex failed to compile in {fname}() function when called by {callfname}() function: {msg}\n.".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
                raise
        
        # Continue with function if regex compiles
        else:
            # Run the named-group regex as a single regex. (This may result in some matches being missed
            # if preceding mathces are found because grouped regexes cannot overlap.)
            if phjSeparateRegexGroups == False:
                # Create a dataframe with a column for each named group in the regex
                phjScratchDF = phjDF[phjDescriptorVarName].str.extract(phjNamedGroupRegex, expand = True)
                
                # Add the descriptor column only from the original dataframe
                phjScratchDF = phjScratchDF.join(phjDF[phjDescriptorVarName])
                
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
                phjScratchDF = phjDF.loc[:,[phjDescriptorVarName]]
                
                for subpattern in re.split('\|\s*(?=\(\?P<)', phjNamedGroupRegexStr):
                    phjGroupRegex = re.compile(subpattern,flags = re.I|re.X)
                    phjGroupName = list(phjGroupRegex.groupindex)[0]
                    
                    phjScratchDF[phjGroupName] = phjScratchDF[phjDescriptorVarName].str.extract(phjGroupRegex,
                                                                                                expand = False)
                    
                    if phjPrintResults == True:
                        print(phjGroupName + ' ... done')
                    else:
                        print('.',end = '')
                        
                print('\n')
            
            # Create a new column that contains a count of the number of matches.
            # Obviously, it should only be 1 but it is possible that a small number of cases
            # may have more than 1 match.
            # Some cases may not be classified.
            phjGroupNamesList = list(phjNamedGroupRegex.groupindex)
            phjScratchDF[phjNumberMatchesVarName] = phjScratchDF[phjGroupNamesList].count(axis = 1)
            
            if phjPrintResults == True:
                # Frequency table showing number of group matches
                print('\nTable of number of group matches identified per description term\n')
                print(pd.DataFrame(phjScratchDF[phjNumberMatchesVarName].value_counts(sort = False)).rename_axis('Number of matches').rename(columns = {phjNumberMatchesVarName:'Frequency'}))
                print('\n')
            
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
                    if grp in phjDF.columns.values:
                        print('One or more group names in the regular expression clash with column headings in the dataframe. In order to avoid confusion, the phjCleanup variable has been set to True.')
                        phjCleanup = True
            
            # Remove the temporary columns before joining with original dataframe.
            if phjCleanup == True:
                phjScratchDF = phjScratchDF.drop(phjGroupNamesList,
                                                 axis = 1)
            
            # Join phjScratchDF to original database
            phjDF = phjDF.join(phjScratchDF.loc[:,phjScratchDF.columns != phjDescriptorVarName],
                                       how = 'left')

            if phjPrintResults == True:
                # Print samples of rows of dataframe
                with pd.option_context('display.max_rows', 20, 'display.max_columns', 20):
                    print(phjDF)
                    print('\n')
    
    return phjDF



def phjMaxLevelOfTaxonomicDetail(phjDF,
                                 phjFirstCol,
                                 phjLastCol,
                                 phjNewColName = 'newColumn',
                                 phjDropPreExisting = False,
                                 phjCleanup = False,
                                 phjPrintResults = False):
    
    # Check function parameters have been set to reasonable values
    try:
        # Check whether required parameters have been set to correct type
        assert isinstance(phjDF,pd.DataFrame), "Parameter 'phjDF' needs to be a Pandas dataframe."
        assert isinstance(phjFirstCol,str), "Argument 'phjFirstCol' needs to be a string."   # In Python 2, use isinstance(s,basestring)
        assert isinstance(phjLastCol,str), "Argument 'phjLastCol' needs to be a string."
        assert isinstance(phjNewColName,str), "Argument 'phjNewColName' needs to be a string."
        
        # Check whether required columns exist
        assert phjFirstCol in phjDF.columns.values, "Column '{0}' is not in dataframe.".format(phjFirstCol)
        assert phjLastCol in phjDF.columns.values, "Column '{0}' is not in dataframe.".format(phjLastCol)
        assert phjDF.columns.get_loc(phjLastCol) - phjDF.columns.get_loc(phjFirstCol) > 0, "Columns are given in the wrong order; '{0}' (phjFirstCol) needs to occur BEFORE '{1}' (phjLastCol) in the dataframe.".format(phjFirstCol,phjLastCol)
        
        # Check whether arguments are set to allowable values
        assert phjDropPreExisting in [True,False], "Argument 'phjDropPreExisting' can only be True or False; it is incorrectly set."
        assert phjCleanup in [True,False], "Argument 'phjCleanup' can only be True or False; it is incorrectly set."
        assert phjPrintResults in [True,False], "Argument 'phjPrintResults' can only be True or False; it is incorrectly set."
        
        # Check whether columns that will be created already exist
        if phjDropPreExisting == False:
            assert 'bin' not in phjDF.columns.values, "A column named 'bin' will be temporarily created but already exists; please rename."
            assert 'posFromR' not in phjDF.columns.values, "A column named 'posFromR' will be temporarily created but already exists; please rename."
            assert phjNewColName not in phjDF.columns.values, "A column named '{0}' (phjNewColName) will be permanently created but already exists; please choose a different name.".format(phjNewColName)
        
    except AssertionError as e:
        print("An AssertionError occurred. ({0})".format(e))
        
    else:
        
        # If columns already exist, drop from dataframe
        if phjDropPreExisting == True:
            if 'bin' in phjDF.columns.values:
                phjDF = phjDF.drop('bin',axis = 1)
            
            if 'posFromR' in phjDF.columns.values:
                phjDF = phjDF.drop('posFromR',axis = 1)
            
            if phjNewColName in phjDF.columns.values:
                phjDF = phjDF.drop(phjNewColName,axis = 1)
        
        
        # A discussion of solutions to convert a dataframe with strings and empty cells to binary is given at:
        # https://stackoverflow.com/questions/49003150/creating-a-binary-representation-of-whether-a-string-is-present-or-not-in-a-pand
        # Several options given.
        # Decided to use a Pandas-based option suggested by jezrael (although Numpy options may be quicker)
        phjRangeOfCols = list(range(phjDF.columns.get_loc(phjFirstCol),
                                    phjDF.columns.get_loc(phjLastCol) + 1))
        
        phjDF['bin'] = (phjDF.iloc[:,phjRangeOfCols] != '').astype(int).astype(str).values.sum(axis=1)
        
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
        #phjDF['posFromR'] = (np.log2(phjDF['bin'].astype(int) & -phjDF['bin'].astype(int)) + 1).astype(int)
        
        
        # If all cells in a row were empty, the binary representation would be 000...000. This causes
        # big problems when trying to calculate the two's complement because log2(0) is infinity.
        # To overcome this problem, add a '1' to start of each string; this won't affect the calculation
        # of the rightmost set bit except in cases where all cells are empty, in which case the rightmost
        # set bit will lie outside the number of columns being considered.
        phjDF['posFromR'] = (np.log2( ('1' + phjDF['bin']).astype(int) & -('1' + phjDF['bin']).astype(int)) + 1).astype(int)
        
        # Count back from the last column to find the column containing the last string entry
        phjDF[phjNewColName] = phjDF.columns[phjDF.columns.get_loc(phjLastCol) - phjDF['posFromR'] + 1]
        
        # If the posFromR value is greater than the number of columns listed then the row of cells
        # must have consisted of all zeroes. Therefore, replace all such occurrences with some
        # indicator e.g. 'unclassified'.
        nCols = phjDF.columns.get_loc(phjLastCol) - phjDF.columns.get_loc(phjFirstCol) + 1
        phjMask = phjDF['posFromR'].astype(int) > nCols
        phjDF.loc[phjMask,phjNewColName] = 'unclassified'
        
        # Remove temporary columns
        if phjCleanup == True:
            phjDF = phjDF.drop(['bin','posFromR'],
                                       axis = 1)
        
        # Print dataframe
        if phjPrintResults == True:
            print(phjDF)
            print('\n')
    
    return phjDF



def phjReverseMap(phjDF,
                  phjMappingDict,
                  phjCategoryVarName,
                  phjMappedVarName = 'mapped_cat',
                  phjUnmapped = np.nan,
                  phjTreatAsRegex = False,
                  phjDropPreExisting = False,
                  phjPrintResults = False):
    
    # Check whether required parameters have been set to correct type
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjMappingDict',phjMappingDict,collections.Mapping)
        phjAssert('phjCategoryVarName',phjCategoryVarName,str,phjMustBePresentColumnList = list(phjDF.columns))
        #phjAssert('phjMappedVarName',phjMappedVarName,str)
        phjAssert('phjUnmapped',phjUnmapped,(str,int,float))
        phjAssert('phjTreatAsRegex',phjTreatAsRegex,bool)
        phjAssert('phjDropPreExisting',phjDropPreExisting,bool)
        
        # Check whether columns that will be created already exist
        if phjDropPreExisting == False:
            phjAssert('phjMappedVarName',phjMappedVarName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
            
            if phjTreatAsRegex == True:
                # If regexes will be used then need to check that numerous other columns
                # are not already in use
                # The following asserts used the phjAssert() function to ensure consistent
                # error messages would be produced even though some functionality was
                # redundant (e.g. testing whether 'numberMatches' is a string is not
                # strictly necessary).
                for col in list(phjMappingDict.keys()):
                    phjAssert('Dictionary key name',col,str,phjMustBeAbsentColumnList = list(phjDF.columns))
                    
                phjAssert('Number of matches','numberMatches',str,phjMustBeAbsentColumnList = list(phjDF.columns))
                
        elif phjDropPreExisting == True:
            # If phjDropPreExisting is True then only need to check that name of the
            # variable is a string value.
            phjAssert('phjMappedVarName',phjMappedVarName,str)
        
        # And almost finally...
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
        # Bespoke asserts
        # ---------------
        # Check that all the items in the dictionary values are uniquely represented, otherwise
        # the dictionary entry will only reflect the last occurrence.
        # Make a flat list of items in the dict values using list comprehension and check there
        # are no duplicates. List comprehension taken from:
        # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
        phjItems = [item for sublist in list(phjMappingDict.values()) for item in sublist]
        assert len(set(phjItems)) == len(phjItems), 'Items in dictionary values are not unique.'
    
    except AssertionError as e:
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
            raise
    
    else:
        if phjTreatAsRegex == True:
            if phjDropPreExisting == True:
                # Drop pre-existing columns.
                # New columns that will be created include:
                #    i. Names of dictionary keys
                #   ii. Column named numberMatches (which is created during function)
                #  iii. Column passed as phjMappedVarName
                
                # Only retain those columns that are not included in the above list of
                # columns that will be created during the function.
                phjOrigCols = list(phjDF.columns)
                phjDF = phjDF[[c for c in phjOrigCols if c not in list(phjMappingDict.keys()) + ['numberMatches',phjMappedVarName]]].copy()
                
                # Print a list of columns that existed in the original dataframe but are not
                # found in dataframe.
                # The following construction prints the list as a series of comma-separated
                # items with the final 2 items separated by 'and'. Hint for achieving this
                # found at: https://stackoverflow.com/questions/2556108/rreplace-how-to-replace-the-last-occurrence-of-an-expression-in-a-string
                if phjPrintResults == True:
                    if set(phjOrigCols) != set(list(phjDF.columns)):
                        print("The following columns already existed in the dataframe and have been dropped: '{}'.".format(' and '.join("', '".join([c for c in phjOrigCols if c not in list(phjDF.columns)]).rsplit(', ',1))))
                        print('\n')
                    
            # The dict as entered is converted to a 'long' format with one regex
            # per row. A named group regex is then created using phjCreateNamedGroupRegex()
            # and matches identified using phjFindRegexNamedGroups().
            # Converting the dictionary to a long dataframe is based on an answer
            # by aws_apprentice at https://stackoverflow.com/questions/54368318/reshaping-a-python-dict-to-a-pandas-dataframe.
            phjRegexDF = pd.DataFrame.from_dict(phjMappingDict, orient='index').stack().reset_index().drop('level_1', axis=1).rename(columns={'level_0': 'key', 0: 'value'})
            
            try:
                phjRegexStr = phjCreateNamedGroupRegex(phjDF = phjRegexDF,
                                                       phjGroupVarName = 'key',
                                                       phjRegexVarName = 'value',
                                                       phjIDVarName = None,
                                                       phjRegexPreCompile = False,
                                                       phjPrintResults = phjPrintResults)
            
            # Catch exception passed from phjCreateNamedGroupRegex() function
            except AssertionError as e:
                # If function has been called directly, present message.
                if inspect.stack()[1][3] == '<module>':
                    print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                             fname = inspect.stack()[0][3]))
                
                # If function has been called by another function then modify message and re-raise exception
                else:
                    print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                                   fname = inspect.stack()[0][3],
                                                                                                                                   callfname = inspect.stack()[1][3]))
                    raise
            
            else:
                try:
                    phjDF = phjFindRegexNamedGroups(phjDF = phjDF,
                                                    phjDescriptorVarName = phjCategoryVarName,
                                                    phjNamedGroupRegexStr = phjRegexStr,
                                                    phjSeparateRegexGroups = True,
                                                    phjNumberMatchesVarName = 'numberMatches',
                                                    phjMatchedGroupVarName = phjMappedVarName,
                                                    phjUnclassifiedStr = phjUnmapped,
                                                    phjMultipleMatchStr = 'multiple',
                                                    phjCleanup = False,
                                                    phjPrintResults = phjPrintResults)
                
                # Re-catch exceptions passed by phjFindRegexNamedGroups() function
                except AssertionError as e:
                    # If function has been called directly, present message.
                    if inspect.stack()[1][3] == '<module>':
                        print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                                 fname = inspect.stack()[0][3]))
                    
                    # If function has been called by another function then modify message and re-raise exception
                    else:
                        print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                                       fname = inspect.stack()[0][3],
                                                                                                                                       callfname = inspect.stack()[1][3]))
                        raise
                        
                except re.error as e:
                    # If function has been called directly, present message.
                    if inspect.stack()[1][3] == '<module>':
                        print("Regex failed to compile in {fname}() function: {msg}\n.".format(msg = e,
                                                                                             fname = inspect.stack()[0][3]))
                    else:
                        # If function has been called by another function then modify message and re-raise exception
                        print("Regex failed to compile in {fname}() function when called by {callfname}() function: {msg}\n.".format(msg = e,
                                                                                                                                   fname = inspect.stack()[0][3],
                                                                                                                                   callfname = inspect.stack()[1][3]))
                        raise
                        
        elif phjTreatAsRegex == False:
            if phjDropPreExisting == True:
                # Drop pre-existing column. In this scenario, only need to remove the
                # column that has the same name as the phjMappedVarName variable
                phjDF = phjDF[[c for c in list(phjDF.columns) if c not in [phjMappedVarName]]].copy()

            # Not treating search strings as regexes.
            # A function to reverse a dict was given in an answer by MSeifert at:
            # https://stackoverflow.com/questions/35491223/inverting-a-dictionary-with-list-values
            # Alternatively, use a dictionary comprehension but must be careful that no duplicates
            # are found in the items in the dictionary values.
            # Taken from: https://stackoverflow.com/questions/37082877/map-pandas-dataframe-columns-to-dictionary-values
            phjRevDict = {v: k for k in phjMappingDict for v in phjMappingDict[k]}
            
            if phjPrintResults == True:
                print("Reversed dictionary\n")
                print(phjRevDict)
                print('\n')
            
            phjDF[phjMappedVarName] = phjDF[phjCategoryVarName].map(phjRevDict).fillna(phjUnmapped)
            
            if phjPrintResults == True:
                print(phjDF)
                print('\n')
    
    finally:
        return phjDF



# This function retrieves unique values of a variable from multiple dataframes and
# concatenates into a single dataframe
def phjRetrieveUniqueFromMultiDataFrames(phjDFList,
                                         phjVarNameList,
                                         phjSort = True,
                                         phjPrintResults = False):
 
    ##########
    # Need to check that phjDFList and phjVarNameList are lists; if strings, need to convert to lists.
    # Check that columns exist.
    ##########
    
    # If phjDFList entered as a dataframe then convert to a list of dataframes (with 1 item)
    if isinstance(phjDFList,pd.DataFrame):
        phjDFList = [phjDFList]

    # If phjVarNameList is a string then convert to a list (with 1 item)
    if isinstance(phjVarNameList,str):
        phjVarNameList = [phjVarNameList]
    
    try:
        # phjDFList needs to be a list of dataframes. If it is confirmed to be a list
        # then check that each item is a dataframe
        phjAssert('phjDFList',phjDFList,list)
        
        for df in phjDFList:
            phjAssert('Element in phjDFList',df,pd.DataFrame)
        
        # phjVarNameList needs to be a list of strings. If it is confirmed to be a list
        # then check that all the listed varnames are present in each dataframe in phjDFList
        phjAssert('phjVarNameList',phjVarNameList,list)
        
        for df in phjDFList:
            phjAssert('phjVarNameList',phjVarNameList,list,phjBespokeMessage = 'The variable names are not present in all dataframes.',phjMustBePresentColumnList = list(df.columns))
        
        # Other asserts
        phjAssert('phjSort',phjSort,bool)
        phjAssert('phjPrintResults',phjPrintResults,bool)
        
    except AssertionError as e:
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
            raise
    
    else:
        
        phjCombDF = pd.DataFrame()
        
        for phjTempDF in phjDFList:
            phjCombDF = pd.concat([phjCombDF,phjTempDF[phjVarNameList].drop_duplicates(keep = 'first')])
        
        phjCombDF = phjCombDF[phjVarNameList].drop_duplicates(keep = 'first').reset_index(drop = True)
        
        if phjSort == True:
            phjCombDF = phjCombDF.sort_values(by = phjVarNameList).reset_index(drop = True)
        
        if phjPrintResults == True:
            for index,df in enumerate(phjDFList):
                print('Unique values in dataframe at position {}'.format(index))
                print(df[phjVarNameList].drop_duplicates())
                print('\n')
                
            print('Dataframe of unique values from all dataframes')
            print(phjCombDF)
        
        if phjCombDF.empty:
            return None
        else:
            return phjCombDF
 
 
 
def phjCreateRowOfValuesForDtypes(phjDF,
                                  phjDtypeDict,
                                  phjScalarBool = True,
                                  phjPrintResults = False):
 
    # This function creates a dict containing column names as keys and appropriate strings
    # or values for the dictionary value.
    #
    # The phjDtypeDict defines what values should be added to columns of specific dtypes
    # such as:
    #    dict = {'object':'missing',
    #            'int64':999}
    #
    # Step through each key in phjDtypeDict and add the associated value to all columns of
    # that dtype.
    # For the following dataframe (with 4 columns of dtypes object, int64, object, int64):
    #       a    b    c    d
    #    0  1  abc  101  jkl
    #    1  2  def  102  mno
    #    2  3  ghi  103  pqr
    #
    # The following dict will be produced:
    #    {'a':999,'b':'missing','c':999,'d':'missing'}
    #
    # (N.B. The same single missing value code is added to all int64 columns. Future update
    # may allow a dictionary of missing value codes to be entered.)
    
    phjOutDict = {}
    
    for key,value in phjDtypeDict.items():
        # Create a dict of column names for each dtype
        phjTempDict = {col:value for col in phjDF if phjDF[col].dtype == key}
        
        # Add phjDict1 to existing phjDict0. Code to add dictionaries taken from:
        # https://stackoverflow.com/questions/6005066/adding-dictionaries-together-python
        phjOutDict = {k: v for d in (phjOutDict, phjTempDict) for k, v in d.items()}
    
    # If scalar values are not required then convert values to lists
    if phjScalarBool == False:
        phjOutDict = {k:[v] for k,v in phjOutDict.items()}
    
    return phjOutDict
 
 
 
def phjDataFrameLowerCase(phjDF,
                          phjVarNameList,
                          phjPrintResults = False):
    
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjVarNameList',phjVarNameList,list,phjMustBePresentColumnList = list(phjDF.columns))
        phjAssert('phjPrintResults',phjPrintResults,bool)

    except AssertionError as e:
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
            raise
    
    else:
        # Create a copy of the dataframe so the original is not edited
        phjDF = phjDF.copy()
        
        # Step through each column of dataframe; if dtype is an object, convert to lowercase
        for phjCol in phjVarNameList:
            if phjDF[phjCol].dtype == 'object':
                phjDF[phjCol] = phjDF[phjCol].str.lower()
        
        return phjDF



# This function updates the lookup tables in the database by appending any new values
# that are included in the data files
def phjUpdateLUT(phjExistDF,
                 phjNewDF,
                 phjIDName,
                 phjVarNameList,
                 phjMissStr,
                 phjMissCode,
                 phjIgnoreCase = True,
                 phjPrintResults = False):
    
    ##########
    # Need to check that both DFs have the same structure
    # Need to check that if phjVarNameList is a list of length 1 then item needs to be a string
    # Need to check that missing value code doesn't clash with pre-existing id value for something that isn't 'missing'.
    ##########
    
    if phjPrintResults == True:
        print('Existing dataframe')
        print('------------------')
        print(phjExistDF)
        print('\n')
        print('New dataframe')
        print('-------------')
        print(phjNewDF)
        print('\n')
    
    # Retain only those entries in phjNewDF that don't already exist in phjExistDF
    # and are not the missing value string (the missing value string and code will
    # be added later if necessary).
    #
    # If the phjVarName parameter is a string (or a list with a single value) then consider
    # the single column as a Series
    if isinstance(phjVarNameList,str) | (isinstance(phjVarNameList,list) & (len(phjVarNameList) == 1)):
        if isinstance(phjVarNameList,list):
            phjVarNameList = phjVarNameList[0]
        
        # This part of code creates a mask to indicate which values in new series already exist
        # in old series (with missing string added)
        if phjIgnoreCase == False:
            phjMask = pd.Series(phjNewDF[phjVarNameList]).isin(phjExistDF[phjVarNameList].append(pd.Series(phjMissStr)))
        
        else:
            phjMask = pd.Series(phjNewDF[phjVarNameList].str.lower()).isin(phjExistDF[phjVarNameList].append(pd.Series(phjMissStr)).str.lower())
        
        phjNewDF = phjNewDF[~phjMask].copy()
    
    # If the phjVarName parameter is a list with greater than one value then consider as a dataframe.
    elif (isinstance(phjVarNameList,list) & (len(phjVarNameList) > 1)):
        # This part of the code creates a mask to determine which values in new dataframe already
        # exist in old dataframe (with missing value and missing string added).
        # Firstly, missing value is added to columns of type int64 and missing string is added to
        # columns of type 'object'
        
        # Define missing values to add to columns of specific dtypes
        phjDtypeDict = {'object':phjMissStr,
                        'int64':phjMissCode}
        
        # Create a row of data (as a dict) containing column names as keys and appropriate
        # missing string or value (depending on dtype of column).
        phjDict0 = phjCreateRowOfValuesForDtypes(phjDF = phjExistDF,
                                                 phjDtypeDict = phjDtypeDict,
                                                 phjScalarBool = True,
                                                 phjPrintResults = phjPrintResults)
        
        # Create mask to determine which rows already exist. Hints to code this taken from:
        # https://stackoverflow.com/questions/60836441/identify-rows-in-pandas-dataframe-that-already-exist
        if phjIgnoreCase == False:
            phjMask = phjNewDF.merge(phjExistDF.append(phjDict0,ignore_index = True),on=phjVarNameList,how='left',indicator=True)['_merge'].eq('both')
        
        else:
            phjMask = phjDataFrameLowerCase(phjDF = phjNewDF,
                                            phjVarNameList = phjVarNameList).merge(phjDataFrameLowerCase(phjDF = phjExistDF.append(phjDict0,ignore_index = True),
                                                                                                         phjVarNameList = phjVarNameList),
                                                                                   on=  phjVarNameList,
                                                                                   how='left',
                                                                                   indicator=True)['_merge'].eq('both')
        
        phjNewDF = phjNewDF[~phjMask].copy()
    
    if phjPrintResults == True:
        print('Dataframe of new values')
        print('-----------------------')
        print(phjNewDF)
        print('\n')
    
    # Create new values for 'id' column that continues on from pre-existing values but does not duplicate
    # missing value code (whatever that might be).
    # Create a list of existing ID values, not including missing value code, and identify the maximum value
    phjIDList = [i for i in phjExistDF[phjIDName] if i not in [phjMissCode]]
    
    # If the list is empty then max value is zero; otherwise the max value is the value returned by max()
    if not phjIDList:
        phjMax = 0
    else:
        phjMax = max(phjIDList)
    
    # Produce list of new ID values (with a couple spare to allow missing value code to be removed
    # if it occurs somewhere in the list)
    phjNewIDList = [n for n in range(phjMax + 1,
                                     phjMax + len(phjNewDF.index) + 2) if n not in [phjMissCode]]
    
    # Number of new items to add
    phjNewIDList = phjNewIDList[:len(phjNewDF.index)]
    
    if phjPrintResults == True:
        print('List of new ID values')
        print('---------------------')
        print(phjNewIDList)
        print('\n')
    
    # Add new ID values as new column to phjNewDF dataframe
    phjNewDF[phjIDName] = phjNewIDList
    
    if phjPrintResults == True:
        print('New dataframe with new ID')
        print('-------------------------')
        print(phjNewDF)
        print('\n')
    
    # If missing value code and string are not present in database then add as a row in
    # phjNewDF dataframe so it can be added to the database along with new items
    if isinstance(phjVarNameList,str) | (isinstance(phjVarNameList,list) & (len(phjVarNameList) == 1)):
        if phjExistDF.loc[(phjExistDF[phjIDName] == phjMissCode) &
                          (phjExistDF[phjVarNameList] == phjMissStr),[phjIDName,phjVarNameList]].empty:
            
            phjNewDF = phjNewDF.append({phjIDName:phjMissCode,
                                        phjVarNameList:phjMissStr},ignore_index = True)
    
    elif (isinstance(phjVarNameList,list) & (len(phjVarNameList) > 1)):
        # For the moment, just check whether the missing value code is found in the ID column
        if phjExistDF.loc[phjExistDF[phjIDName] == phjMissCode,:].empty:
            # Add the phjDict0 created previously as the new row
            phjNewDF = phjNewDF.append(phjDict0,ignore_index = True)
    
    phjNewDF = phjNewDF.sort_values(by = [phjIDName]).reset_index(drop = True)
    
    if phjPrintResults == True:
        print('Returned dataframe')
        print('------------------')
        print(phjNewDF)
        print('\n')
    
    return phjNewDF



# This function is designed to update LUT tables based on new values
# but maintaining existing id numbers
def phjUpdateLUTToLatestValues(phjDF,
                               phjIDVarName,
                               phjGroupbyVarName,
                               phjAddCountCol = True,
                               phjPrintResults = False):
    
    ######
    # Check values are correctly entered
    # Check 'n' column does not already exist
    ######
    
    #####
    # Could add different column on which to sort (e.g. date)
    #####
    
    # Add count column to indicate how many rows in each groupby group
    if phjAddCountCol == True:
        phjDF['n'] = phjDF.groupby(phjGroupbyVarName)[phjGroupbyVarName].transform('count')
    
    # Keep record of column order
    phjColOrder = [c for c in phjDF]
    
    # Make sure dataframe is ordered based on grouping variable and id variable
    phjDF = phjDF.sort_values(by = [phjGroupbyVarName,phjIDVarName]).copy()
    
    if phjPrintResults == True:
        if 'n' in phjDF:
            print('Original sorted dataframe with count variable')
            print('---------------------------------------------')
        else:
            print('Original sorted dataframe')
            print('-------------------------')

        print(phjDF)
        print('\n')
    

    # The aim of this function is to retain the first row of data (i.e. pre-existing) for the id (and name) column and
    # the final row of data for everything else. This could be done using agg() function and pass a dictionary to indicate
    # which colunms to extract first rows and which columns to extract the final rows, for example:
    #    df.groupby('name').agg({'id':'first','name':'last'})
    # However, the 'first' and 'last' methods don't handle NaN values and will ignore them. Instead, use different methods,
    # namely nth(0) and nth(-1). Not clear how to implement nth() methods because defining a dictionary did not work.
    # Use work-around, namely divide dataframe into two sections (by column), select relevant information and rejoin.
    
    # For phjIDVarName and phjGroupbyVarName columns, select the first rows (i.e. the rows that already exist in the dataframe)
    phjOutDF_pti =  phjDF[[c for c in phjDF if c in [phjIDVarName,phjGroupbyVarName]]].groupby(phjGroupbyVarName).nth(0).reset_index(drop = False)
    
    # For all other columns (including the grouping variable), select the final row (i.e. the most recent data to be added)
    phjOutDF_ptii = phjDF[[c for c in phjDF if c not in [phjIDVarName]]].groupby(phjGroupbyVarName).nth(-1).reset_index(drop = False)
    
    # Rejoin dataframes based on grouping variable
    phjOutDF = phjOutDF_pti.merge(phjOutDF_ptii, on = phjGroupbyVarName)
    
    # Rearrange order of columns to match original
    phjOutDF = phjOutDF[[c for c in phjColOrder if c in phjOutDF]]
    
    if phjPrintResults == True:
        print('Updated dataframe')
        print('-----------------')
        print(phjOutDF)
        print('\n')
        
    return phjOutDF
    
    

if __name__ == '__main__':
    main()

