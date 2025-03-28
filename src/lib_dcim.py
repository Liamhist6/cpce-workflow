import json
import pytz
import exiftool
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

from .PathManager import PathManager
from .lib_tools import linear_interpolation

def time_calibration_and_geotag(path_manager: PathManager):

    # Get metadata of frames
    with exiftool.ExifTool(common_args=["-n"]) as et:
        json_frames_metadata = et.execute(*[f"-j", "-fileorder", "filename", str(path_manager.dcim_folder)])

    if json_frames_metadata == "":
        print("No images with metadata")
        return
    
    # Format metadata.
    csv_exiftool_frames = pd.DataFrame.from_dict(json.loads(json_frames_metadata))
    
    keep_param_list = [
        "ApertureValue", "Compression", "Contrast", "CreateDate", "DateCreated", "DateTimeDigitized", "DigitalZoomRatio", "ExifImageHeight", "ExifImageWidth", 
        "ExifToolVersion", "ExifVersion", "ExposureCompensation", "ExposureMode", "ExposureProgram", "FileName", "FileSize", "FileType", "FileTypeExtension", "FNumber", 
        "FocalLength", "FocalLength35efl", "FocalLengthIn35mmFormat", "FOV", "GPSAltitude", "GPSAltitudeRef", "GPSDateTime", "GPSDate", "GPSTime", "GPSLatitude", "GPSLongitude",
        "GPSMapDatum", "GPSPosition", "GPSTimeStamp", "GPSRoll", "GPSPitch", "GPSTrack", "ImageHeight", "ImageWidth", "LightValue", "Make", "MaxApertureValue", 
        "MaximumShutterAngle", "Megapixels", "MeteringMode", "MIMEType", "Model", "Saturation", "ScaleFactor35efl", "SceneCaptureType", "SceneType", "SensingMethod", "Sharpness", 
        "ShutterSpeed", "Software", "SubSecDateTimeOriginal", "ThumbnailLength", "ThumbnailOffset", "WhiteBalance", "XResolution", "YResolution", "GPSfix", "GPSsdne", "GPSsde", "GPSsdn"
    ]

    intersection_list = [col for col in csv_exiftool_frames.columns if col in keep_param_list]

    csv_exiftool_frames = csv_exiftool_frames[intersection_list]
    csv_exiftool_frames["relative_file_path"] = csv_exiftool_frames["FileName"].apply(lambda x : str(Path(path_manager.session_path.name, "DCIM", x)))


    gps_dataframe = pd.read_csv(path_manager.gps_dataframe_path)


    def find_gps_position(row):
        dt = datetime.strptime(row["SubSecDateTimeOriginal"], "%Y:%m:%d %H:%M:%S%z")
        dt_utc_timestamp = dt.astimezone(timezone.utc).timestamp()

        lower_row = gps_dataframe[gps_dataframe["datetime_unix"] <= dt_utc_timestamp].iloc[-1]
        higher_row = gps_dataframe[gps_dataframe["datetime_unix"] >= dt_utc_timestamp].iloc[0]

        if all(lower_row == higher_row):
            return f'{lower_row["GPSLatitude"]}, {lower_row["GPSLongitude"]}'
        else:
            lat_interp = linear_interpolation(lower_row["GPSLatitude"], higher_row["GPSLatitude"], lower_row["datetime_unix"], higher_row["datetime_unix"], dt_utc_timestamp)
            lon_interp = linear_interpolation(lower_row["GPSLongitude"], higher_row["GPSLongitude"], lower_row["datetime_unix"], higher_row["datetime_unix"], dt_utc_timestamp)
            return f'{lat_interp}, {lon_interp}'


    csv_exiftool_frames["GPSPosition"] = csv_exiftool_frames.apply(lambda x: find_gps_position(x), axis=1)
    csv_exiftool_frames["GPSLatitude"] = csv_exiftool_frames.apply(lambda x: x["GPSPosition"].split(", ")[0], axis=1)
    csv_exiftool_frames["GPSLongitude"] = csv_exiftool_frames.apply(lambda x: x["GPSPosition"].split(", ")[1], axis=1)

    csv_exiftool_frames.to_csv(path_manager.metadata_filepath, index=False)
    
    