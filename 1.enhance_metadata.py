import shutil
from datetime import datetime
import traceback
import pandas as pd
from pathlib import Path
from natsort import natsorted

from src.utils import populate_annotation, get_code_benthic

DATASET = Path("F:/", "CLEAN_DATA")

def main():

    if not DATASET.exists() or not DATASET.is_dir():
        print("Dataset does not exist", DATASET)
        return
    
    codes_benthic = get_code_benthic(Path("CPCe_benthic_codes_mada.txt"))

    for session in sorted(list(DATASET.iterdir())):
        try:
            print(f"Processing session {session}")

            CPCE_FOLDER = Path(session, "PROCESSED_DATA", "CPCE_ANNOTATION")
            if not CPCE_FOLDER.exists() or not CPCE_FOLDER.is_dir():
                print(f"{CPCE_FOLDER} not found")
                continue

            metadata_path = Path(session, "METADATA", "metadata.csv")
            metadata_path2 = Path(session, "METADATA", "metadata2.csv")

            if not metadata_path.exists() or not metadata_path.is_file():
                print(f"{metadata_path} not found")
                continue

            metadata_df = pd.read_csv(metadata_path)
            
            metadata_df = populate_annotation(CPCE_FOLDER, metadata_df, codes_benthic)
            metadata_df.to_csv(metadata_path2, index=False)
                
            print(f"Session {session.name} processed successfully.\n")
        except Exception as e:
            print(f"Error processing {session.name}: {e}")
            print(traceback.format_exc(), end="\n\n")
        
        break

if __name__ == "__main__":
    main()
