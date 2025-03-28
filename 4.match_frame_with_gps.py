import argparse
import traceback

from src.lib_gps import compute_gps
from src.PathManager import PathManager
from src.lib_dcim import time_calibration_and_geotag
from src.lib_tools import print_header, get_list_sessions


def parse_args():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description="Amoros workflow", epilog="Thanks to use it!")

    # Input.
    arg_input = parser.add_mutually_exclusive_group(required=True)
    arg_input.add_argument("-efol", "--enable_folder", action="store_true", help="Use folder of session")
    arg_input.add_argument("-eses", "--enable_session", action="store_true", help="Unique session")
    arg_input.add_argument("-ecsv", "--enable_csv", action="store_true", help="Parse session from csv file")

    # Path of input.
    parser.add_argument("-pfol", "--path_folder", default="F:\\CLEAN_DATA", help="Load all images from a folder of sessions")
    parser.add_argument("-pses", "--path_session", default="F:\\CLEAN_DATA\\20240119_MDG-Toliara_UVC-01_04", help="Load all images from a single session")
    parser.add_argument("-pcsv", "--path_csv_file", default="csv/amoros.csv", help="Path to csv file")

    # Options.
    parser.add_argument("-c", "--cleaning", action="store_true", help="Clean processed files.")

    return parser.parse_args()


def main(opt):

    print_header()

    list_sessions = get_list_sessions(opt)
    session_name_fails = []

    for session in list_sessions:
        print("\n\n-- Launching " + session.name)

        try:
            path_manager = PathManager(session, opt.cleaning)

            ### Compute GPS
            compute_gps(path_manager)

            ### Extract image metadata
            time_calibration_and_geotag(path_manager)
        
        except Exception:
            # Print error
            print(traceback.format_exc(), end="\n\n")
            
            # Store sessions name
            session_name_fails.append(session.name)

    # Stat.
    print("\n\nEnd of process. On {} sessions, {} fails. ".format(len(list_sessions), len(session_name_fails)))
    if (len(session_name_fails)):
        [print("\t* " + session_name) for session_name in session_name_fails]

if __name__ == "__main__":
    opt = parse_args()
    main(opt)