# -*- coding: utf-8 -*-

import sys
from Instances import * 
#from SNOPCompactModel import SNOPCompactModel
from VND import VND
from RVND import RVND
from GVNS import GVNS
from MetaData import MetaData
from SNOPSolutionInplaceBuilder import SNOPSolutionInplaceBuilder
from SNOPSolutionOutOfPlaceBuilder import SNOPSOlutionOutOfPlaceBuilder
from SNOPSolutionDjikstraValueBuilder import SNOPSolutionDjikstraValueBuilder
import os
import cProfile
import pstats
import functools
from MCI import MCI

import concurrent.futures 

model = MCI(N=100)



def run_SNOP_Exact(file : str, time_limit: int, recursive : bool, save_file : str) -> None:
    if not os.path.isdir(file) or not recursive:
        print(file,time_limit)
        edges = read_instance(file)
        instance = Instance(edges)
        
        model.construct_model(instance)
        metadata = model.solve(time_limit=time_limit)

        #cProfile.run("model.solve()")
        save_file = save_file if save_file else 'solve.dat'
        with open(save_file,'a') as f:
            f.write(f"Name: {file}\n")
            f.write(f"Resolution time:{metadata.resolution_time}\n")
            f.write(f"Value:{metadata.objective_value}\n")
            #f.write(f"first value:{metadata.misc['first_value']}\n")
            #f.write(f"Gap:{metadata.misc['Gap']}\n\n\n")
            f.write("\n\n")
    else:
        if os.path.isdir(file):
           
            with concurrent.futures.ProcessPoolExecutor() as executor:
                executor.map(functools.partial(run_SNOP_Exact,time_limit=time_limit,recursive=recursive,save_file=save_file),
                            [os.path.join(file,f) for f in os.listdir(file) if os.path.isfile(os.path.join(file,f))])
            
            if recursive:
                for f in os.listdir(file):
                    file_path = os.path.join(file,f)
                    if os.path.isdir(file_path):
                        run_SNOP_Exact(file_path,time_limit,recursive,save_file)
            
            """for f in os.listdir(file):
                file_path = os.path.join(file,f)
                if (os.path.isdir(file_path) and recursive) or os.path.isfile(file_path):
                    run_SNOP_Exact(file_path,time_limit,recursive,save_file)
            """


if __name__ == "__main__":
    try: 
        assert len(sys.argv) > 1
    except AssertionError:
            print("Requires arguments",file=sys.stderr)
        
    arg_counter = 1
    arg1 = sys.argv[arg_counter]
    arguments = ""

    recursive = False
    save_file = ""
    time_limit = float("inf")


    if (arg1[0] == '-'):  # argument
        arguments = arg1[1:]
        arg_counter += 1
    
    files = sys.argv[arg_counter:]

    try:
        assert len(files) >= 1
    except AssertionError:
        print("Requires arguments",file=sys.stderr)
        sys.exit(1)
    
    for c in arguments:
        if c == 'r' :
            recursive = True
        if c== 't':
            time_limit = int(files[0])
            print(time_limit)
            files.pop(0)
        if c == 's':
            save_file = files[0]
            files.pop(0)


    random.seed(0)
    for file in files:
        run_SNOP_Exact(file,time_limit,recursive,save_file)
        """with cProfile.Profile() as profile:
            print(f"{file}")
            run_SNOP_Exact(file,time_limit,recursive,save_file)
            

        results = pstats.Stats(profile)
        results.sort_stats(pstats.SortKey.TIME)
        results.print_stats()
        results.dump_stats("resultsOutplace.prof")"""