import shutil
from pathlib import Path

class PathManager:

    def __init__(self, session_path: Path, needCleaning: bool) -> None:
        self.session_path = session_path
        self.cleaning = needCleaning


        self.dcim_folder = Path(session_path, "DCIM")
        self.metadata_folder = Path(session_path, "METADATA")
        self.gps_device_folder = Path(session_path, "GPS", "DEVICE")
        self.cpce_annotation_folder = Path(session_path, "PROCESSED_DATA", "CPCE_ANNOTATION")


        self.prog_json_path = Path(self.metadata_folder, "prog_config.json")

        self.gps_dataframe_path = Path(self.gps_device_folder, "gps_data.csv")
        self.metadata_filepath = Path(self.metadata_folder, "metadata.csv")

        self.setup()
    
    def setup(self) -> None:

        if not self.session_path.exists() or not self.session_path.is_dir():
            raise NameError(f"[ERROR] Session path {self.session_path} not found") 

        if not self.dcim_folder.exists() or not self.dcim_folder.is_dir():
            raise NameError(f"[ERROR] DCIM folder {self.dcim_folder} not found") 
        
        if len(list(self.dcim_folder.iterdir())) == 0:
            raise NameError(f"[ERROR] DCIM folder is empty") 
        
        if not self.gps_device_folder.exists() or not self.gps_device_folder.is_dir():
            raise NameError(f"[ERROR] GPS Device folder {self.gps_device_folder} not found") 
        
        if self.cleaning:
            if self.metadata_folder.exists():
                shutil.rmtree(self.metadata_folder)

            for file in self.gps_device_folder.iterdir():
                if file.suffix != ".gpx":
                    print(f"Removing {file}")
                    file.unlink()

        
        self.metadata_folder.mkdir(exist_ok=True)