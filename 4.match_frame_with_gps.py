import csv
import json
import shutil
import argparse
import traceback
from pathlib import Path

from src.lib_tools import print_header
from src.lib_gps import compute_gps
from src.PathManager import PathManager
from src.lib_dcim import time_calibration_and_geotag


def parse_args():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description="Rename benthic code file in cpc files", epilog="Thanks to use it!")


    parser.add_argument("-csv", default=None, help="Path to csv file for session_name")
    parser.add_argument("-rp", "--root_path", default=None, help="Root path for the session")
    parser.add_argument("-cn", "--config_path", default="config/config.json", help="Path to the config file to use")


    return parser.parse_args()


def main(opt):

    print_header()

    # Open json file with config of the session
    default_config_path = opt.config_path if opt.config_path != None else "./config/config.json"
    with open(default_config_path) as json_file:
        cfg_prog = json.load(json_file)

    # Override root path
    if opt.root_path:
        cfg_prog["session_info"]["root"] = opt.root_path


    # Build a list of [SESSION_NAME, FIRST_FRAME_UTC, LAST_FRAME_UTC]
    listSessionFirstFrame = [[
        cfg_prog['session_info']['session_name'], 
        str(cfg_prog['dcim']['time_first_frame_UTC']), 
        str(cfg_prog['dcim']['time_last_frame_UTC'])
    ]]

    DEFAULT_SIZE = len(listSessionFirstFrame[0])
    if opt.csv != None and Path(opt.csv).exists():
        with open(opt.csv, "r") as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            header = next(spamreader, None)
            listSessionFirstFrame = [row if len(row) == DEFAULT_SIZE else row + [""] * (DEFAULT_SIZE - len(row)) for row in spamreader]

    
    session_name_fails = []
    # Go over all file from session_csv
    for session_name, time_first_frame, time_last_frame in listSessionFirstFrame:
        print("\n\n-- Launching " + session_name)

        # Create and verify if session folder exists and setup all pass
        try:
        
            session_path = Path(cfg_prog["session_info"]["root"], session_name)
            need_cleaning = cfg_prog['session_info']['delete_processed_session']
            path_manager = PathManager(session_path, need_cleaning)
        
        except Exception:
            print(traceback.format_exc(), end="\n\n")
            
            # Store sessions name
            session_name_fails.append(session_name)
            continue

        try:
            # Change session_name in cfg_prog else we have bad name
            cfg_prog['session_info']['session_name'] = session_name 

            ### Compute GPS
            compute_gps(path_manager)

            ### Extract image metadata
            time_calibration_and_geotag(path_manager)
        
        except Exception:
            # Print error
            print(traceback.format_exc(), end="\n\n")
            
            # Store sessions name
            session_name_fails.append(session_name)
        
        finally:
            # Always write config in METADATA folder
            print("\n-- Finally, save config.json\n")
            with open(path_manager.prog_json_path, 'w') as fp:
                json.dump(cfg_prog, fp,indent=3)
    
    # Stat.
    print("End of process. On {} sessions, {} fails. ".format(len(listSessionFirstFrame), len(session_name_fails)))
    if (len(session_name_fails)):
        [print("\t* " + session_name) for session_name in session_name_fails]

if __name__ == "__main__":
    opt = parse_args()
    main(opt)