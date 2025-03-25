import argparse
from pathlib import Path
# Demander à l'utilisateur ce qu'il veut:
#    - un dossier de session
#   - une session

# Demander le chemin de stockage du fichier et si il est pas rempli 

DATASET = Path("F:/", "CLEAN_DATA")

def parse_args():

    # Parse command line arguments.
    ap = argparse.ArgumentParser(description="Rename benthic code file in cpc files", epilog="Thanks to use it!")

    # Input.
    arg_input = ap.add_mutually_exclusive_group(required=True)
    arg_input.add_argument("-efol", "--enable_folder", action="store_true", help="Use folder of session")
    arg_input.add_argument("-eses", "--enable_session", action="store_true", help="Unique sessionsession")

    # Path of input.
    ap.add_argument("-pfol", "--path_folder", default="F:\\CLEAN_DATA", help="Load all images from a folder of sessions")
    ap.add_argument("-pses", "--path_session", default="F:\\CLEAN_DATA\\20240119_MDG-Toliara_UVC-01_04", help="Load all images from a single session")

    return ap.parse_args()


def main(opt):

    sessions = []
    if opt.enable_folder:
        path_session_folder = Path(opt.path_folder)
        if not path_session_folder.exists() or not path_session_folder.is_dir(): raise NameError(f"Folder not found for {path_session_folder}")
        sessions = [s for s in sorted(list(path_session_folder.iterdir())) if s.is_dir()]
    elif opt.enable_session:
        path_session_folder = Path(opt.path_session)
        if not path_session_folder.exists() or not path_session_folder.is_dir(): raise NameError(f"Folder not found for {path_session_folder}")
        sessions.append(path_session_folder)
        

    for session in sessions:
        print(f"Working with {session}")

        cpce_folder = Path(session, "PROCESSED_DATA", "CPCE_ANNOTATION")
        if not cpce_folder.exists():
            print(f"Benthic file code not found for: {cpce_folder}")


        cpce_benthic_file = Path(session, "PROCESSED_DATA", "CPCE_ANNOTATION", "cpce_codes_mada_40.txt")
        if not cpce_benthic_file.exists():
            print(f"Benthic file code not found for: {cpce_benthic_file}")

        for file in sorted(list(cpce_folder.iterdir())):
            if file.suffix.lower() not in ['.cpc']: continue
            
            with open(file, "r", encoding="latin-1") as f:
                lines = f.readlines()
            
            if not lines: continue

            numbers = lines[0].split(',')[1:]
            lines[0] = f'"{str(cpce_benthic_file)}",{','.join(numbers)}'

            with open(file, "w", encoding="latin-1") as f:
                f.writelines(lines)


if __name__ == "__main__":
    opt = parse_args()
    main(opt)