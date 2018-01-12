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



def phjGetStrFromArgOrFile(phjStr = None,
                           phjPathAndFileName = None,
                           phjAllowedAttempts = 3,
                           phjPrintResults = False):
    
    # This function retrieves a string either from a string contained in a text file
    # given by a path and file name, or from a string entered as an argument for this
    # function. A string saved in a file is given preference (i.e. this is checked first).
    
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
        
        else:
            phjTempStr = None
        
        # If the text file did not yield a string, move on to the query string.
        if (phjTempStr is None) and (phjStr is not None):
            phjTempStr = phjStr
            
            if phjPrintResults == True:
                print("\nString retrieved from passed argument (phjStr):")
                print(phjTempStr)
            
        else:
            phjTempStr = None
            
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
            phjTempFileObject = open(phjFilePathAndName)
            phjTempText = phjTempFileObject.read()
            phjTempFileObject.close()
            
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



if __name__ == '__main__':
    main()

