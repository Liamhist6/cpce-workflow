import shutil
import traceback
import pandas as pd
from pathlib import Path
from datetime import datetime
from natsort import natsorted

from src.utils import get_cpce_folder, get_frame_folder, get_coordinates, match_framename_cpce_file

DATASET = Path("F:/", "cpce-workflow-victor", "dataset", "raw_data_aina", "raw_data")
OUTPUT_DIR = Path("F:/", "CLEAN_DATA")
CPCE_CODE = Path("CPCe_benthic_codes_mada.txt")

def main():
    if not DATASET.exists() or not DATASET.is_dir():
        print("Dataset does not exist", DATASET)
        return

    seen = {}
    for place in list(DATASET.iterdir())[::-1]:
        for transect_name in natsorted(list(place.iterdir())):
            try:
                print(f"Processing transect {transect_name}")

                cpce_path = get_cpce_folder(transect_name)
                frame_path = get_frame_folder(transect_name)
                coordinates = get_coordinates(transect_name)

                if coordinates.empty:
                    raise NameError(f"No coordinates found for {transect_name}")

                coordinates_with_cpce_link = match_framename_cpce_file(coordinates, cpce_path)

                if coordinates_with_cpce_link.empty:
                    raise NameError("No matching CPCe files found")

                date = coordinates_with_cpce_link.iloc[0]["Date"]
                formatted_date = datetime.strptime(date, "%d/%m/%Y %H:%M:%S").strftime("%Y%m%d")
                base_session_name = f"{formatted_date}_MDG-{place.name}_UVC-01"
                seen[base_session_name] = seen.get(base_session_name, 0) + 1

                session_number = str(seen[base_session_name]).rjust(2, '0')
                session_name = f"{base_session_name}_{session_number}"
                session_path = Path(OUTPUT_DIR, session_name)

                if session_path.exists() and session_path.is_dir():
                    shutil.rmtree(session_path)

                dcim_folder = Path(session_path, "DCIM")
                metadata_folder = Path(session_path, "METADATA")
                cpce_folder = Path(session_path, "PROCESSED_DATA", "CPCE_ANNOTATION")
                
                for folder in [dcim_folder, metadata_folder, cpce_folder]:
                    folder.mkdir(exist_ok=True, parents=True)

                shutil.copy(CPCE_CODE, cpce_folder / CPCE_CODE.name)

                metadata_rows, frames_file_content = [], []
                
                for i, row in coordinates_with_cpce_link.iterrows():
                    img_path = frame_path / f'{row["FileName"]}.JPG'
                    if not img_path.exists():
                        print(f"File {img_path} does not exist.")
                        continue

                    shutil.copy(img_path, dcim_folder / img_path.name)

                    cpce_file_in = Path(row["cpce_file"])
                    cpce_file_out = cpce_folder / cpce_file_in.name

                    shutil.copy(cpce_file_in, cpce_file_out)
                    
                    with open(cpce_file_out, "r", encoding="latin-1") as file:
                        lines = file.readlines()
                    
                    if lines:
                        numbers = lines[0].split(',')[2:]
                        lines[0] = f'"{cpce_folder / CPCE_CODE.name}","../../DCIM/{img_path.name}",{','.join(numbers)}'
                        with open(cpce_file_out, "w", encoding="latin-1") as f:
                            f.writelines(lines)
                    
                    image_number = str(i + 1).rjust(4, '0')
                    file_name = f"{formatted_date}_MDG-{place.name}_UVC-01_{session_number}_{image_number}.jpeg"
                    relative_file_path = f"{session_name}/DCIM/{img_path.name}"
                    datetime_formatted = datetime.strptime(row["Date"], "%d/%m/%Y %H:%M:%S").strftime("%Y:%m:%d %H:%M:%S")

                    metadata_row = {
                        "OriginalFileName": img_path.name,
                        "FileName": file_name,
                        "GPSLatitude": row["Latitude"],
                        "GPSLongitude": row["Longitude"],
                        "DateTime": datetime_formatted,
                        "relative_file_path": relative_file_path
                    }

                    metadata_rows.append(metadata_row)
                    frames_file_content.append(relative_file_path)

                metadata_df = pd.DataFrame(metadata_rows)
                metadata_df.to_csv(metadata_folder / "metadata.csv", index=False)
                
                print(f"Session {session_name} processed successfully.\n")
            except Exception as e:
                print(f"Error processing {transect_name}: {e}")
                print(traceback.format_exc(), end="\n\n")
            

if __name__ == "__main__":
    main()
