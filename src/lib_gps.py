import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from .PathManager import PathManager

def parse_gpx(file_path: Path) -> dict:
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    namespace = {
        "gpx": "http://www.topografix.com/GPX/1/1",
        "gpxx": "http://www.garmin.com/xmlschemas/GpxExtensions/v3",
        "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    }
    
    track_data = []
    
    for trkpt in root.findall(".//gpx:trkpt", namespace):
        lat = trkpt.get("lat")
        lon = trkpt.get("lon")
        ele = trkpt.find("gpx:ele", namespace).text if trkpt.find("gpx:ele", namespace) is not None else None
        time = trkpt.find("gpx:time", namespace).text if trkpt.find("gpx:time", namespace) is not None else None
        
        track_data.append({
            "GPSLatitude": float(lat),
            "GPSLongitude": float(lon),
            "GPSElevation": float(ele) if ele else None,
            "GPSDatetime": time
        })
    
    return track_data


def compute_gps(path_manager: PathManager) -> None:

    print("Parsing GPX file.")

    # Try to find the gpx file.
    gpx_filepath = None
    for file in path_manager.gps_device_folder.iterdir():
        if file.suffix != ".gpx": continue
        
        gpx_filepath = file
        break

    # If we don't found the gpx file, return
    if gpx_filepath == None: return

    track_data = parse_gpx(gpx_filepath)

    df_gps = pd.DataFrame(track_data).sort_values(by=["GPSDatetime"])
    df_gps["GPSDatetime"] = df_gps.apply(lambda x: " ".join(x['GPSDatetime'].replace('-', ':').replace('Z', '').split('T')), axis=1)
    df_gps["datetime_unix"] = df_gps['GPSDatetime'].apply(lambda x: datetime.strptime(x, "%Y:%m:%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    
    df_gps.to_csv(path_manager.gps_dataframe_path, index=False)


