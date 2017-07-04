"""
Functions to check postcode variable in Pandas dataframe
========================================================

These functions take a dataframe containing postcode information and attempts
to correct errors and extract outward (first half), inward (second half) and
postcode area (first letters) components of the postcode.

"""

# Import required packages
# ========================

import re

import pkg_resources


try:
    pkg_resources.get_distribution('numpy')
except pkg_resources.DistributionNotFound:
    phjNumpyPresent = False
    print("Error: Numpy package not available.")
else:
    phjNumpyPresent = True
    import numpy as np


try:
    pkg_resources.get_distribution('pandas')
except pkg_resources.DistributionNotFound:
    phjPandasPresent = False
    print("Error: Pandas package not available.")
else:
    phjPandasPresent = True
    import pandas as pd



# Define functions to check UK postcodes
# ======================================

def phjCleanUKPostcodeVariable(phjTempDF,
                               phjOrigPostcodeVarName = 'postcode',
                               phjNewPostcodeVarName = 'postcodeClean',
                               phjPostcodeFormatCheckVarName = 'postcodeFormatCheck',
                               phjMissingValueCode = 'missing',
                               phjPostcode7VarName = 'postcode7',
                               phjPostcodeAreaVarName = 'postcodeArea',
                               phjSalvageOutwardPostcodeComponent = True,
                               phjDropExisting = False,
                               phjPrintResults = True):
    
    if phjMissingValueCode is None:
        # The missing value code can not be np.nan because the DataFrame.update() function will
        # not update NaN values and, as a result, some changes are likely to be missed.
        print('Missing value code can not be NaN. Please re-run the function with a string value.')
        
    else:
        # Create a working dataframe containing postcode variable only and
        # making sure that new columns that will be created (e.g. to store cleaned
        # postcodes) don't already exist. If phjDropExisting is set to True,
        # pre-existing columns will be dropped.
        phjTempWorkingDF = phjCreateWorkingPostcodeDF(phjTempDF = phjTempDF,
                                                      phjOrigPostcodeVarName = phjOrigPostcodeVarName,
                                                      phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                      phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                      phjPostcode7VarName = phjPostcode7VarName,
                                                      phjPostcodeAreaVarName = phjPostcodeAreaVarName,
                                                      phjDropExisting = phjDropExisting,
                                                      phjPrintResults = phjPrintResults)
        
        
        # Only continue to clean-up postcode values if a valid working directory is returned.
        if phjTempWorkingDF is not None:
            # Some basic clean-up house-keeping
            phjTempWorkingDF = phjUKPostcodeBasicCleanUp(phjTempDF = phjTempWorkingDF,
                                                         phjOrigPostcodeVarName = phjOrigPostcodeVarName,
                                                         phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                         phjMissingValueCode = phjMissingValueCode,
                                                         phjPrintResults = phjPrintResults)
            
            
            # Identify correctly (and incorrectly) formatted postcodes
            phjTempWorkingDF = phjUKPostcodeFormatCheck(phjTempDF = phjTempWorkingDF,
                                                        phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                        phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                        phjPrintResults = phjPrintResults)
            
            
            if phjPrintResults == True:
                print("\nCorrectly and incorrectly formatted postcodes (BEFORE ERROR CORRECTION):")
                print(phjTempWorkingDF.loc[phjTempWorkingDF[phjNewPostcodeVarName].notnull(),phjPostcodeFormatCheckVarName].value_counts())
                print(phjTempWorkingDF)
                print('\n')
            
            
            # Deal with postcode entries that do not match postcode regex (i.e. not formatted correctly)
            phjTempWorkingDF = phjUKPostcodeCorrectCommonErrors(phjTempDF = phjTempWorkingDF,
                                                                phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                                phjPrintResults = phjPrintResults)
            
            
            if phjPrintResults == True:
                print("\nCorrectly and incorrectly formatted postcodes (AFTER ERROR CORRECTION):")
                print(phjTempWorkingDF.loc[phjTempWorkingDF[phjNewPostcodeVarName].notnull(),phjPostcodeFormatCheckVarName].value_counts())
                print(phjTempWorkingDF)
                print('\n')
            
            
            # Produce variable containing 7-character postcode
            phjTempWorkingDF = phjPostcodeFormat7(phjTempDF = phjTempWorkingDF,
                                                  phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                  phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                  phjPostcode7VarName = phjPostcode7VarName,
                                                  phjPrintResults = phjPrintResults)
            
            
            print(phjTempWorkingDF)
            # Create variables containing outward and inward parts of postcode
            phjTempWorkingDF = phjExtractPostcodeComponents(phjTempDF = phjTempWorkingDF,
                                                            phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                            phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                            phjPrintResults = phjPrintResults)
            
            
            if phjSalvageOutwardPostcodeComponent == True:
                # Some postcode entries may be just the outward part of the postcode (e.g. NP4, CH64, etc.).
                # Such entries will not be identified as a correctly formatted postcode but it may be possible
                # to salvage some information on the postcode district.
                # To salvage postcode district, the string could only be 2, 3 or 4 characters long.
                # Error correction will be applied and the format of the resulting string tested using the
                # postcodeOutward group of the regular expression.
                phjTempWorkingDF = phjSalvagePostcode(phjTempDF = phjTempWorkingDF,
                                                      phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                      phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                      phjPrintResults = phjPrintResults)
                
                
                # Extract postcode area from postcodeOutward variable
                phjTempWorkingDF = phjExtractPostcodeArea(phjTempDF = phjTempWorkingDF,
                                                          phjPostcodeAreaVarName = phjPostcodeAreaVarName,
                                                          phjPrintResults = phjPrintResults)
            
            
            if phjPrintResults == True:
                print('\nFinal working postcode dataframe\n================================\n')
                print(phjTempWorkingDF)
                print('\n')
            
            
            # Drop original postcode column from phjTempWorkingDF and add new columns to original dataframe
            phjTempWorkingDF = phjTempWorkingDF.drop(phjOrigPostcodeVarName, axis = 1)
            
            for phjCol in phjTempWorkingDF.columns:
                if phjCol in phjTempDF.columns:
                    phjTempDF = phjTempDF.drop(phjCol,axis=1)
            
            phjTempDF = phjTempDF.join(phjTempWorkingDF)
            
            
            # Finally, copy missing value code to postcodeClean variable if no postcode format has been extracted
            phjTempDF.loc[phjTempDF[phjPostcodeFormatCheckVarName] == False,phjNewPostcodeVarName] = phjMissingValueCode
    
    
    # If a valid working dataframe was created then changes would have been made in above code
    # and copied to phjTempDF.
    # If working dataframe was not valid, then no changes would have been made and phjTempDF
    # would remain unaltered.
    # Either way, return phjTempDF.
    return phjTempDF



def phjCreateWorkingPostcodeDF(phjTempDF,
                               phjOrigPostcodeVarName,
                               phjNewPostcodeVarName,
                               phjPostcodeFormatCheckVarName,
                               phjPostcode7VarName,
                               phjPostcodeAreaVarName,
                               phjDropExisting = False,
                               phjPrintResults = False):
    
    # Creates working directory if postcode variable exists and other variables either don't exist or can be deleted.
    # If not, the function returns None.
    
    # Check that named postcode variable actually exists...
    if phjOrigPostcodeVarName in phjTempDF.columns:
    
        # Retrieve list of names of regex groups
        phjRegexGroupNamesList = phjGetPostcodeRegexGroupNamesList(phjPrintResults = False)
        
        # Check whether new variables already exist and drop if have permission
        phjVarCounter = 0
        for phjVarName in [phjNewPostcodeVarName,
                           phjPostcodeFormatCheckVarName,
                           phjPostcode7VarName,
                           phjPostcodeAreaVarName] + phjRegexGroupNamesList:
            if phjVarName in phjTempDF.columns:
                if phjDropExisting:
                    # Drop if have permission to do so...
                    phjTempDF = phjTempDF.drop(phjVarName,axis = 1)
                    print("Column '{0}' needs to be added to the dataframe but the variable already exists; the pre-existing column has been reset.".format(phjVarName))
                else:
                    # ...otherwise, return None
                    print("Column '{0}' needs to be added to the dataframe but the variable already exists; please delete the column and re-run the function.".format(phjVarName))
                    phjVarCounter = phjVarCounter + 1
                    
        if phjVarCounter > 0:
            phjTempDF = None
            
    else:
        # If postcode variable does not exist, return None
        print('Variable', phjOrigPostcodeVarName,'does not exist in the dataframe. This variable should contain the original postcode data.')
        phjTempDF = None
    
    # Working dataframe only needs the original postcode variable, and some additional empty columns
    if phjTempDF is not None:
        phjTempDF = phjTempDF.loc[:,[phjOrigPostcodeVarName,
                                     phjNewPostcodeVarName,
                                     phjPostcodeFormatCheckVarName]]
        
    return phjTempDF



def phjUKPostcodeBasicCleanUp(phjTempDF,
                              phjOrigPostcodeVarName,
                              phjNewPostcodeVarName,
                              phjMissingValueCode = 'missing',
                              phjPrintResults = False):
    
    # Copy original postcode data to new variable
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjOrigPostcodeVarName]
    
    # Replace Python None values with Pandas phjMissingValueCode in original postcode variable
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].fillna(value = phjMissingValueCode)
    
    # Strip white space and punctuation and convert postcode text to all uppercase
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace('''[\W_]+''',value='',regex = True)
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].str.upper()
    
    # Empty cells should be replaced with missing value code.
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace('',value = phjMissingValueCode,regex = False)
    
    # Replace cells containing indication of missing or unknown with missing value code.
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace(re.compile('''^[\W_]*mis+i?n?g?[\W_]*$''',flags=re.I),value = phjMissingValueCode,regex = True)
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace(re.compile('''^[\W_]*(?:un|not)[\W_]*(?:k?nown)[\W_]*$''',flags=re.I),value = phjMissingValueCode,regex = True)
    
    # Postcodes that consist of all numbers should be changed to missing value code.
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace(re.compile('''^\s*\d+\s*$'''),value = phjMissingValueCode,regex = True)
    
    return phjTempDF



def phjUKPostcodeRegexDefinition(phjPrintResults = False):
    # The following Regex was taken from https://en.wikipedia.org/wiki/Talk:Postcodes_in_the_United_Kingdom
    # (accessed 22 Mar 2016). The page is also stored as PDF entitled:
    # "Talk/Postcodes in the United Kingdom - Wikipedia, the free encyclopedia".
    # Regex was originally given as:
    # '(GIR 0AA)|(((A[BL]|B[ABDFHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9]|((E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(SW|W)([2-9]|[1-9][0-9])|EC[1-9][0-9]) [0-9][ABD-HJLNP-UW-Z]{2})'
    # However, this was modified slightly to allow for optional space between first and second
    # parts of postcode (even though all the whitespace has been removed in an earlier
    # step (see above) and restricting to beginning and end of string.
    # A new binary variable is created that contains 1 = correctly formated postcode and
    # 0 = incorrectly formatted postcode.
    # (N.B. The original did not find old Norwich postcodes of the form NOR number-number-letter
    # or old Newport postcodes of form NPT number-letter-letter but updated version does. Also,
    # the inward component changed to include 'V' in order to pick up NPT 0VA. Also, changed outward
    # regex to pick up W1 (as in W1 3PF) and WC99 (as in WC99 0LF and WC99 9AP.)
    # In the latest modification, the regex was changed so it consisted of two named components
    # recognising the outward (first half) and inward (second half) of the postcode. These
    # were compiled into a single regex, separated by whitespace (even though white space is
    # removed from the string before processing).

    postcodeOutwardRegex = '''(?P<postcodeOutward>(?:^GIR(?=\s*0AA$)) |                 # Identifies special postcode GIR 0AA
                                                  (?:^NOR(?=\s*[0-9][0-9][A-Z]$)) |     # Identifies old Norwich postcodes of format NOR number-number-letter
                                                  (?:^NPT(?=\s*[0-9][A-Z][A-Z]$)) |     # Identifies old Newport (South Wales) postcodes of format NPT number-letter-letter
                                                  (?:^(?:(?:A[BL]|B[ABDFHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9] |  # Identifies stardard outward code e.g. L4, L12, CH5, CH64
                                                      (?:(?:E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(?:SW|W)(?:[1-9]|[1-9][0-9])|EC[1-9][0-9]|WC99))    # Identifies the odd London-based postcodes
                               )'''
    
    postcodeInwardRegex = '''(?P<postcodeInward>(?<=NOR)(?:\s*[0-9][0-9][A-Z]$) |      # Picks out the unusual format of old Norwich postcodes (including leading space)
                                                (?:[0-9][ABD-HJLNP-UVW-Z]{2}$)         # Picks out standard number-letter-letter end of postcode
                             )'''
    
    # KNOWN ISSUES
    # ============
    # The inward part of old Norwich postcodes may be returned with preceding white space.
    # This was because look behind can not be of variable length and, therefore, the
    # option of variable which space needed to be included in the captured group.
    #
    # The letter-letter combination in NPT areas currently allows all possible combinations
    # but this should be defined better.
    
    
    if phjPrintResults == True:
        print('\nOutward regex\n-------------\n{0}'.format(postcodeOutwardRegex))
        print('\nInward regex\n------------\n{0}'.format(postcodeInwardRegex))
        print('\n')
        
    return [postcodeOutwardRegex,postcodeInwardRegex]



def phjUKPostcodeRegexDefinition_DavidSingleton2017(phjPrintResults = False):
    # The following Regex was used by David Singleton and was originally given as:
    # ^((GIR 0AA)|((([A-PR-UWYZ][A-HK-Y]?[0-9][0-9]?)|(([A-PR-UWYZ][0-9][A-HJKSTUW])|([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV-Y]))) [0-9][ABD-HJLNP-UW-Z]{2}))$
    
    postcodeOutwardRegex = '''(?P<postcodeOutward>(?:^GIR(?=\s*0AA$)) |                 # Identifies special postcode GIR 0AA
                                                  (?:^(?:[A-PR-UWYZ][A-HK-Y]?[0-9][0-9]?)|(?:(?:[A-PR-UWYZ][0-9][A-HJKSTUW])|(?:[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV-Y])))
                               )'''
    
    postcodeInwardRegex = '''(?P<postcodeInward>(?:[0-9][ABD-HJLNP-UW-Z]{2}$)
                             )'''
    
    # KNOWN ISSUES
    # ============
    # Does not pick up old Norwich or Newport postcodes.
    # Does not pick up some London postcodes.
    
    
    if phjPrintResults == True:
        print('\nOutward regex\n-------------\n{0}'.format(postcodeOutwardRegex))
        print('\nInward regex\n------------\n{0}'.format(postcodeInwardRegex))
        print('\n')
        
    return [postcodeOutwardRegex,postcodeInwardRegex]



def phjGetPostcodeRegexGroupNamesList(phjPrintResults = False):
    # This function returns the names of regex groups as a list with the outward name first
    # and the inward name second.
    # Need to retrieve names from individual compiled regexes and add names to list one at a
    # time. If retrieve group names from complete regex in one go then the resulting
    # dictionary will contain names in unpredictable order (i.e. outward
    # group name may be after inward group name).
    postcodeOutwardRegex, postcodeInwardRegex = phjUKPostcodeRegexDefinition(phjPrintResults = False)
    
    postcodeOutwardRegex = re.compile(postcodeOutwardRegex,flags = re.I|re.X)
    postcodeOutwardRegexList = [k for k in postcodeOutwardRegex.groupindex.keys()]

    postcodeInwardRegex = re.compile(postcodeInwardRegex,flags = re.I|re.X)
    postcodeInwardRegexList = [k for k in postcodeInwardRegex.groupindex.keys()]
    
    # Combine into single list with outward name in first position and inward name in second position.
    phjRegexGroupNamesList = postcodeOutwardRegexList + postcodeInwardRegexList

    return phjRegexGroupNamesList



def phjGetCompiledPostcodeRegex(phjPostcodeComponent = 'all',
                                phjPrintResults = False):
    
    # This function returns returns a compiled regex for either the whole postcode regex
    # or a component of the postcode regex (outward or inward)
    
    # Retrieve postcode regex definitions for outward and inward parts and compile
    phjPostcodeOutwardRegex, phjPostcodeInwardRegex = phjUKPostcodeRegexDefinition(phjPrintResults = False)
    
    if phjPostcodeComponent == 'all':
        phjCompiledPostcodeRegex = re.compile(phjPostcodeOutwardRegex + '\s*' + phjPostcodeInwardRegex,flags = re.I|re.X)
    
    elif phjPostcodeComponent == 'outward':
        phjCompiledPostcodeRegex = re.compile(phjPostcodeOutwardRegex,flags = re.I|re.X)

    elif phjPostcodeComponent == 'inward':
        phjCompiledPostcodeRegex = re.compile(phjPostcodeInwardRegex,flags = re.I|re.X)

    else:
        print('phjPostcodeComponent option is invalid.')
        phjCompiledPostcodeRegex = None
    
    return phjCompiledPostcodeRegex



def phjUKPostcodeFormatCheck(phjTempDF,
                             phjNewPostcodeVarName,
                             phjPostcodeFormatCheckVarName,
                             phjPostcodeComponent = 'all',
                             phjPrintResults = False):
    
    # This function creates a column in the passed dataframe that indicates (True or False)
    # whether the postcode string matches the regex format. The regex used for matching can
    # be either the whole regex or a component (outward or inward).
    phjCompiledPostcodeRegex = phjGetCompiledPostcodeRegex(phjPostcodeComponent = phjPostcodeComponent,
                                                           phjPrintResults = False)
    
    # If the postcode string format matches the regex, enter True in phjPostcodeFormatCheckVarName; else
    # enter False.
    if phjCompiledPostcodeRegex is not None:
        phjTempDF[phjPostcodeFormatCheckVarName] = phjTempDF[phjNewPostcodeVarName].str.contains(phjCompiledPostcodeRegex,na = False)
    
    return phjTempDF



def phjExtractPostcodeComponents(phjTempDF,
                                 phjNewPostcodeVarName,
                                 phjPostcodeFormatCheckVarName,
                                 phjPostcodeComponent = 'all',
                                 phjPrintResults = False):
    
    # This function returns postcode components from a variable containing postcode strings
    # based on named groups in the postcode regex.
    
    # Retrieve postcode regex definition names and compiled regex for appropriate postcode components.
    postcodeOutwardRegex, postcodeInwardRegex = phjUKPostcodeRegexDefinition(phjPrintResults = False)
    phjCompiledPostcodeRegex = phjGetCompiledPostcodeRegex(phjPostcodeComponent = phjPostcodeComponent,
                                                           phjPrintResults = False)
    
    # Create a temporary dataframe that contains extracted postcode components
    phjPostcodeComponentsDF = phjTempDF.loc[phjTempDF[phjPostcodeFormatCheckVarName] == True,phjNewPostcodeVarName].str.extract(phjCompiledPostcodeRegex,
                                                                                                                                expand = True)
    # Add extracted postcode component(s) to original dataframe.
    # If the columns containing extracted data already exist in the database, then the
    # DataFrame.update() function can be used to update non-NA values. This may occur if,
    # for example, the function has already been run on a slice of the original dataframe.
    # If the columns do not already exist, then need to add new columns using DataFrame.join().
    # New columns are added one column at a time to avoid theoretical issues where one column
    # exists and the other does not.
    for phjCol in phjPostcodeComponentsDF.columns:
        if phjCol in phjTempDF.columns:
            phjTempDF.update(phjPostcodeComponentsDF.loc[:,[phjCol]])
        else:
            phjTempDF = phjTempDF.join(phjPostcodeComponentsDF.loc[:,[phjCol]])
    
    return phjTempDF



def phjUKPostcodeCorrectCommonErrors(phjTempDF,
                                     phjNewPostcodeVarName,
                                     phjPostcodeFormatCheckVarName,
                                     phjMissingValueCode = 'missing',
                                     phjPrintResults = False):
    
    # Creates a temporary dataframe containing incorrectly formatted postcodes only.
    # Common errors will be corrected and merged back to the original dataframe.
    phjTempUnformattedDF = phjTempDF.loc[(phjTempDF[phjPostcodeFormatCheckVarName] == False) &
                                         (phjTempDF[phjNewPostcodeVarName].notnull()),[phjNewPostcodeVarName,phjPostcodeFormatCheckVarName]]
    
    phjTempUnformattedDF[phjNewPostcodeVarName] = phjTempUnformattedDF[phjNewPostcodeVarName].map(lambda x: phjCorrectPostcodeErrors(x,
                                                                                                                                     phjMissingValueCode = phjMissingValueCode,
                                                                                                                                     phjRun = 1))
    
    # Check if new postcode strings match the regex format
    # and, if so, set phjPostcodeFormatCheckVarName to True
    phjTempUnformattedDF = phjUKPostcodeFormatCheck(phjTempDF = phjTempUnformattedDF,
                                                    phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                    phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                    phjPostcodeComponent = 'all',
                                                    phjPrintResults = phjPrintResults)
    
    
    # Update dataframe with newly corrected postcode strings. However, DataFrame.update() does not
    # update values that have been returned as NaN and, therefore, the missing value code must not
    # be set to np.nan.
    phjTempDF.update(phjTempUnformattedDF)
    
    return phjTempDF



def phjCorrectPostcodeErrors(x,
                             phjMissingValueCode = 'missing',
                             phjRun = 1):
    
    # This function is called by a lambda function. The lambda function steps through
    # postcode strings and substitutions are made at specific positions based on a
    # lookup dictionary.
    # N.B. The phjRun variable is not currently used but allows the option for several
    # rounds of error-corrections (using different lookup dictionaries) to be made
    # to try to salvage correctly formatted postcode strings (if required).
    
    # Make sure the postcode string does not contain white space or punctuation (this
    # should have already been done but, hey, belt and braces.)
    x = re.sub(r'''[\W_]+''','',x)
    
    # Convert string to list
    phjStrList = list(x)
    
    # Define dictionary of alpha->num and num->alpha conversions.
    # It would probably be better to define this outside the lambda
    # function so the dictionary does not have to be defined repeatedly.
    phjPostcodeReplacementsDict = {'alpha2num': {'I': '1',
                                                 'L': '1',
                                                 'O': '0',
                                                 'S': '5',
                                                 'Z': '2'},
                                   'num2alpha': {'0': 'O',
                                                 '1': 'I',
                                                 '2': 'Z',
                                                 '5': 'S'} }
    
    # If string is 5-7 characters long, it is possible that the
    # postcode has been entered incorrectly. Therefore, try to correct
    # any common errors.
    if (len(x)>=5 and len(x)<=7):
        
        # Inward part of postcode (i.e. second half)
        # -----------------------
        # (The final 3 characters should be number-letter-letter.)
        
        # Third character from end (i.e. first character of inward part) should be a number
        phjStrList[-3] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[-3],phjStrList[-3])
        
        # Second character from end and final character should be letters
        phjStrList[-2] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[-2],phjStrList[-2])
        phjStrList[-1] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[-1],phjStrList[-1])
        
        # Outward part of postcode (i.e. first half of postcode)
        # ------------------------
        # First character (index=0) should always be a letter; assume this is always entered as a letter.
        if len(x)==5:
            # If string is 5 characters long then second character (index=1) should be a number
            phjStrList[1] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[1],phjStrList[1])
            
        elif len(x)==6:
            # Second character (index=1) could be either a letter or a number - therefore, leave unchanged.
            # Third character (index=2) should be a number
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            
        else:
            # Second character (index=1) should be a letter
            # Third character (index=2) should be a number
            # Fourth character (index=3) should be a number
            phjStrList[1] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[1],phjStrList[1])
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            phjStrList[3] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[3],phjStrList[3])
        
        phjReturnStr = ''.join(phjStrList)
        
        
    elif (len(x)>=2 and len(x)<=4):
        # This could be the outward part of the postcode
        # First character (index=0) should always be a letter; assume this is always entered as a letter.
        if len(x)==2:
            # If string is 2 characters long then second character (index=1) should be a number
            phjStrList[1] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[1],phjStrList[1])
            
        elif len(x)==3:
            # Second character (index=1) could be either a letter or a number - therefore, leave unchanged.
            # Third character (index=2) should be a number
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            
        else:
            # Second character (index=1) should be a letter
            # Third character (index=2) should be a number
            # Fourth character (index=3) should be a number
            phjStrList[1] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[1],phjStrList[1])
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            phjStrList[3] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[3],phjStrList[3])
            
        phjReturnStr = ''.join(phjStrList)
        
    else:
        # Postcode strings that are 1 character long or greater than 7 characters (excluding
        # white space and punctuation) are probably beyond all hope and are treated as missing.
        phjReturnStr = phjMissingValueCode
        
    return phjReturnStr



def phjPostcodeFormat7(phjTempDF,
                       phjNewPostcodeVarName,
                       phjPostcodeFormatCheckVarName,
                       phjPostcode7VarName,
                       phjPrintResults = False):
    
    # This function creates a variable containing correctly formatted whole postcodes
    # in 7-character format. This format is commonly used in lookup tables that link
    # postcodes to other geographical data.
    
    # Copy correctly formatted WHOLE postcode strings to postcode7 variable
    phjTempDF[phjPostcode7VarName] = phjTempDF.loc[(phjTempDF[phjPostcodeFormatCheckVarName] == True) &
                                                   (phjTempDF[phjNewPostcodeVarName].str.len() >= 5) &
                                                   (phjTempDF[phjNewPostcodeVarName].str.len() <= 7),phjNewPostcodeVarName]
    
    # Reformat postcode7 variable to 7 characters
    phjTempDF[phjPostcode7VarName] = phjTempDF[phjPostcode7VarName].str.replace(' ','').str.replace('(\w{3})$',r' \1').str.replace('^(\w{2}\s)',r'\1 ').str.replace('^(\w{4})\s',r'\1')
    
    return phjTempDF



def phjSalvagePostcode(phjTempDF,
                       phjNewPostcodeVarName,
                       phjPostcodeFormatCheckVarName,
                       phjMissingValueCode = 'missing',
                       phjPrintResults = False):
    
    phjNumberOfCorrectionRuns = 3
    
    # Create a temporary dataframe containing hitherto incorrectly formatted postcodes only.
    # Common errors will be corrected and outward postcode component will be test to determine
    # whether format is correct.
    phjTempUnformattedDF = phjTempDF.loc[(phjTempDF[phjPostcodeFormatCheckVarName] == False) &
                                         (phjTempDF[phjNewPostcodeVarName].notnull()),[phjNewPostcodeVarName,
                                                                                       phjPostcodeFormatCheckVarName]].copy()
    
    for i in range(1,phjNumberOfCorrectionRuns+1):
        # Create a scatch dataframe consisting of postcode entries that are not matched with regex (in this
        # case, just the outward component).
        phjTempScratchDF = phjTempUnformattedDF.loc[phjTempUnformattedDF[phjPostcodeFormatCheckVarName] == False,:].copy()

        # Check if the incorrectly formatted postcode contains a valid outward postcode component at the start.
        # If so, the phjPostcodeFormatCheckVarName variable will be set to True.
        phjTempScratchDF = phjUKPostcodeFormatCheck(phjTempDF = phjTempScratchDF,
                                                    phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                    phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                    phjPostcodeComponent = 'outward',
                                                    phjPrintResults = False)

        if i < phjNumberOfCorrectionRuns:
            # Correct common errors in postcodes that are still recorded as incorrectly formatted
            phjTempScratchDF[phjNewPostcodeVarName] = phjTempScratchDF[phjNewPostcodeVarName].map(lambda x: phjCorrectPostcodeErrors(x,
                                                                                                                                     phjMissingValueCode = phjMissingValueCode,
                                                                                                                                     phjRun = i))
        
        # Update phjTempUnformattedDF with changed variables in nphjTempScratchDF.
        # N.B. The DataFrame.updata() function does NOT update non
        phjTempUnformattedDF.update(phjTempScratchDF)
        
    # Update postcodeOutward variable with extracted contents of phjNewPostcodeVarName if format
    # matches with outward regex
    phjTempUnformattedDF = phjExtractPostcodeComponents(phjTempDF = phjTempUnformattedDF,
                                                        phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                        phjPostcodeFormatCheckVarName = phjPostcodeFormatCheckVarName,
                                                        phjPostcodeComponent = 'outward',
                                                        phjPrintResults = False)
    
    
    # If unformatted postcode strings have a correctly formatted outward postcode component extracted
    # from the original string, then the extracted string should be copied to the postcodeClean variable.
    
    # Retrieve postcode regex definition names.
    phjRegexGroupNamesList = phjGetPostcodeRegexGroupNamesList(phjPrintResults = False)
    
    if phjRegexGroupNamesList[0] in phjTempUnformattedDF.columns:
        phjTempUnformattedDF.loc[phjTempUnformattedDF[phjPostcodeFormatCheckVarName] == True,phjNewPostcodeVarName] = phjTempUnformattedDF[phjRegexGroupNamesList[0]]
    
    
    # Update dataframe with newly corrected columns (phjNewPostcodeVarName and phjPostcodeFormatCheckVarName)
    phjTempDF.update(phjTempUnformattedDF)
    
    return phjTempDF



def phjExtractPostcodeArea(phjTempDF,
                           phjPostcodeAreaVarName,
                           phjPrintResults):
    
    # Retrieve list of names of regex groups and identify name of outward postcode variable
    phjRegexGroupNamesList = phjGetPostcodeRegexGroupNamesList(phjPrintResults = False)
    phjPostcodeOutwardVarName = phjRegexGroupNamesList[0]
    
    phjTempDF[phjPostcodeAreaVarName] = phjTempDF[phjPostcodeOutwardVarName].str.extract(re.compile('''(^[A-Z]+)''',flags=re.I),
                                                                                         expand = True)
    
    return phjTempDF



if __name__ == '__main__':
    main()
