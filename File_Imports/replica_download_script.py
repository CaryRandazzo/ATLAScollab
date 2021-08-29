def proc_rucDL_text(filename):
  
    """
    
    Processes the text file containing lines of rucio download files in the form <scope>:<did>, one per line
    
    """

    with open(filename, "r+") as f:
        # here, position is initially at the beginning
        text = f.read()
        # now its at the end of this file
    with open(filename+"_processed",'w') as f:
        for line in text.split('\n'):
            f.write('rucio download '+ line + '\n')

    return
