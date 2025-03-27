import shutil
import argparse
from pathlib import Path
from natsort import natsorted

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
        dcim_folder = Path(session, "DCIM")

        if not dcim_folder.exists():
            print(f"DCIM folder not found for: {dcim_folder}")
            continue

        if not cpce_folder.exists():
            print(f"CPCe folder not found for: {cpce_folder}")
            continue

        cpce_benthic_file = Path(cpce_folder, "cpce_codes_mada_40.txt")
        if not cpce_benthic_file.exists():
            print(f"Benthic file code not found for: {cpce_benthic_file}")
            continue
        

        list_images = natsorted(list(dcim_folder.iterdir()))
        for i, image in enumerate(list_images):
            
            # Rename image name.
            image_number = str(i + 1).rjust(4, '0')
            new_image_name = Path(dcim_folder, f"{session.name}_{image_number}{image.suffix}")
            shutil.move(image, new_image_name)


            cpc_file = Path(cpce_folder, f"{image.stem}.cpc")
            new_cpce_file = Path(cpce_folder, f"{new_image_name.stem}.cpc")
            
            if not cpc_file.exists(): continue

            shutil.move(cpc_file, new_cpce_file)

            
            with open(new_cpce_file, "r", encoding="latin-1") as f:
                lines = f.readlines()
            
            if not lines: continue

            numbers = lines[0].split(',')[2:]
            lines[0] = f'"{str(cpce_benthic_file)}","../../DCIM/{new_image_name.name}",{','.join(numbers)}'

            with open(new_cpce_file, "w", encoding="latin-1") as f:
                f.writelines(lines)


if __name__ == "__main__":
    opt = parse_args()
    main(opt)