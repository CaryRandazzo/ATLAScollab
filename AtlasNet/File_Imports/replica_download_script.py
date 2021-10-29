def what_replicas_to_request(input_filename, stream)    :
    """
    
    !IMPORTANT - THIS FUNCTION REQUIRES UPDATE TO MATCH proc function below!
    
    Rucio requests take a specific format. This takes the lines we processed previously in postprocessed_hist_file() and turns the lines into the individual requests needed from rucio
    with their appropriate format.
    
    EXAMPLE FORMAT for a data18_hi request:
        data18_hi:data18_hi.00366526.express_express.merge.HIST.f1030_h333
    
    EXAMPLE USE:
        input_filename = 'backups/green_hists_of_interest/express_good_hists2.txt'
        stream = 'express'
        
    EXAMPLE OUTPUT:
        data18_hi:data18_hi.00366142.express_express.merge.HIST.f1027_h331
        ...etc like this
    
    """
    
    # Determine the format of the stream for the request
    if stream == 'express':
        stream = 'express_express'
    elif stream == 'physics_Main':
        stream = 'physics_Main'  
    elif stream == 'pMain':
        stream = 'physics_Main'
        
    
    # Open the file that contains the final processed histograms and meta information
    with open(input_filename) as f:    
    
        reqs = []
        
        # Read through each line of the file
        for line in f.readlines():
            
            
            # Remove the return characters
            line = line.replace('\n','')
            
            # If this line contains run in it, it must be a 'run-line'
            if 'run' in line:
                
                # So get a handle for the different pieces of this run-line
                line = line.split(' ')
                
                # The run, then is line[0]
                run = line[0]
                
                # The ftag, then is line[1]
                ftag = line[1]
                
                # And the energy then is line[2] (in the unfortunate first time formatting of this file some energy was left blank and all were data18_hi so handle this)
                try:
                    energy = line[2]
                except:
                    energy = 'data18_hi'
                    
                # Print the appropriate request format depending on the energy type
                if '/1' in ftag or '/2' in ftag or '/3' in ftag or '/4' in ftag:
                    print('ftags with /# are not able to be requested from rucio? Dont get these! --->',ftag)
                    continue
                else:
                    reqs.append(f"{energy}:{energy}.00{run.replace('/','').replace('run_','')}.{stream}.merge.HIST.{ftag}")

                
        # Display the number of requests we will have to make
        print(f'Number of Requests: {len(set(reqs})')
        return set(reqs)

def proc_what_replicas_to_request(input_filename, stream):
    
    """
    
    What happens when this function is executed?:
        This function will create an output file using input_filename where input_filename has had all the leading path string information stripped such that all
        will be left will be of a format similar to the following:  output_filename = redhists2_preprocessed.txt and the file will be sent to the same directory the 
        notebook is in. Read further to determine the EXAMPLE OUTPUT inside the output file.
        
    This takes a hand made text file and stream string in as input. Line by line it is formatted as either 
    1. a blank line
    2. a line that includes the  "<ftag> <energy>" or "<ftag>" and energy will be assumed to be 'data18_13TeV'
    3. a histogram path line (run_######/etc/etc/hist_name)
    
    This function will then convert each line to the scope request format that will be needed to request the runs from rucio or lxplus/rucio.
    
    *USE THIS FUNCTION IF YOU HAVE FORMATTED IT ACCORDING TO THE ABOVE, use the other function (what_replicas_to_request()) if it is in the form
    1. blank lines
    2. <run> <ftag> <energy> or <run> <ftag> with energy set as default
    3. a histogram path line (run_######/etc/etc/hist_name)
    
    EXAMPLE FORMAT for a data18_hi request:
        data18_hi:data18_hi.00366526.express_express.merge.HIST.f1030_h333
    
    EXAMPLE USE:
        input_filename = '../Replicas/Scripts&Records/backups/red_hists_of_interest/redhists2.txt'
        stream = 'express'
        reqs = proc_what_replicas_to_request(input_filename, stream)
        
    EXAMPLE OUTPUT:
        data18_hi:data18_hi.00366142.express_express.merge.HIST.f1027_h331
        ...etc like this
    
    """
    
    # Determine the format of the stream for the request
    if stream == 'express':
        stream = 'express_express'
    elif stream == 'physics_Main':
        stream = 'physics_Main'  
    elif stream == 'pMain':
        stream = 'physics_Main'
        
    
    # Open the file that contains the final processed histograms and meta information
    with open(input_filename) as f:    
        
        reqs = []
    
        # Read through each line of the file
        for line in f.readlines():
            
            
            # Remove the return characters
            line = line.replace('\n','')
            
            if 'run' not in line:
                
                line = line.split(' ')
                
                ftag = line[0]
                
                try:
                    energy = line[1]
                except:
                    energy = 'data18_13TeV'
                
            if 'run' in line:
                
                run = line.split('/')[0].split('_')[1]
                
                if '/1' in ftag or '/2' in ftag or '/3' in ftag or '/4' in ftag:
                    print('ftags with /# are not able to be requested from rucio? Dont get these! --->',ftag)
                    continue
                else:
                    reqs.append(f"{energy}:{energy}.00{run.replace('/','').replace('run_','')}.{stream}.merge.HIST.{ftag}")
            
                
        # Display the number of requests we will have to make
        
        reqs = set(reqs)
        print(f'Number of Requests: {len((reqs))}')
        
        # Create the output file with _preprocessed at the end of the name and write the lines from reqs to the file                                 
        with open(input_filename.split('/')[-1].replace('.txt','')+'_preprocessed.txt', "w") as txt_file:
            for line in list(reqs):
                txt_file.write(line + "\n")
        

def proc_rucDL_text(filename):
  
    """
    
    Processes the text file containing lines of rucio download files in the form <scope>:<did>, one per line
    
    """

    with open(filename, "r+") as f:
        # here, position is initially at the beginning
        text = f.read()
        # now its at the end of this file
    with open(filename.replace('.txt','').replace('_preprocessed','')+"_processed.txt",'w') as f:
        for line in text.split('\n'):
            
            # This ignores the ending blank line in the _preprocessed.txt file
            if line=='':
                continue
            
            # Write the line to the output file with the 'rucio download' command added                             
            f.write('rucio download '+ line + '\n')
