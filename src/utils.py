import shutil
import traceback
import pandas as pd
import geopandas as gpd
from pathlib import Path
from natsort import natsorted

def get_cpce_folder(transect_path: Path) -> Path:

    cpce_path = Path(transect_path, "cpce")
    if Path.exists(cpce_path) and cpce_path.is_dir(): return cpce_path

    cpce_path = Path(transect_path, "CPCE")
    if Path.exists(cpce_path) and cpce_path.is_dir(): return cpce_path

    cpce_path = Path(transect_path, "cpce data")
    if Path.exists(cpce_path) and cpce_path.is_dir(): return cpce_path
    
    cpce_path = Path(transect_path, "Output", "cpce")
    if Path.exists(cpce_path) and cpce_path.is_dir(): return cpce_path

    raise NameError(f"CPCE folder not found {cpce_path}")

def get_frame_folder(transect_path: Path) -> Path:
    
    for frame_name in transect_path.iterdir():
        if frame_name.is_file() and frame_name.suffix.lower() == ".jpg":
            return transect_path

    # Try a deeper level.
    output_path = Path(transect_path, "Output")
    if Path.exists(output_path) and output_path.is_dir():
        for file in output_path.iterdir():
            if file.suffix.lower() == ".jpg":
                return output_path
    
    raise NameError(f"Frame path not found for {transect_path}")


def get_coordinates(transect_name: Path):

    coordinate = frame_shp(transect_name)
    if len(coordinate) == 0:
        coordinate = frame_coordinate(transect_name)

    return coordinate

def frame_coordinate(transect_name: Path):

    coordinate_file = None
    for file in transect_name.iterdir():
        if file.name in ["Coordonnée.xlsx", f"{transect_name.name}.xlsx"]:
            coordinate_file = file
            break
    
    if coordinate_file == None: return {}


    frame_folder = get_frame_folder(transect_name)

    df = pd.read_excel(coordinate_file)

    df["relative_file_path"] = df.apply(lambda x: f"{frame_folder}/{x['Name']}.JPG", axis=1)

    return df[["Name", "relative_file_path", "Date", "Latitude", "Longitude"]]

def frame_shp(transect_name: Path):

    shp_file = None
    for file in transect_name.iterdir():
        if file.suffix.lower() in [".shp"]:
            shp_file = file
            break
        
    if shp_file == None:
        temp_path =  Path(transect_name, "Output")
        if temp_path.exists():
            for file in temp_path.iterdir():
                if file.suffix.lower() in [".shp"]:
                    shp_file = file
                    break
    
    if shp_file == None:
        temp_path =  Path(transect_name, "Coordonnée")
        if temp_path.exists():
            for file in temp_path.iterdir():
                if file.suffix.lower() in [".shp"]:
                    shp_file = file
                    break
        
    if shp_file == None: return {}
    df = gpd.read_file(shp_file)

    if len(df) == 0: return {}
    
    if "Image" not in df:
        df["Image"] = df.apply(lambda x: f"{x['Name']}.JPG", axis=1)
    frame_folder = get_frame_folder(transect_name)

    df["relative_file_path"] = df.apply(lambda x: f"{frame_folder}/{x['Image']}", axis=1)

    return df[["Name", "relative_file_path", "Date", "Latitude", "Longitude"]]

def match_framename_cpce_file(coordinates: pd.DataFrame, cpce_path: Path):
    coordinates_2 = coordinates.set_index("Name").to_dict('index')

    for file in natsorted(list(cpce_path.iterdir())):
        filename = file.stem.replace(".", "")

        if filename not in coordinates_2: continue

        if file.is_dir():
            cpce_file = Path(file, f"{filename}.cpc")
            if Path.exists(cpce_file) and cpce_file.is_file():
                coordinates_2[filename]["cpce_file"] = str(cpce_file)
        if file.is_file() and file.suffix == ".cpc":
            coordinates_2[filename]["cpce_file"] = str(file)
    
    [coordinates_2.pop(key) for key in [img for img in coordinates_2 if "cpce_file" not in coordinates_2[img]]]

    return pd.DataFrame.from_dict(coordinates_2, "index").reset_index().rename(columns={"index": "FileName"})

def populate_annotation(cpce_folder: Path, df_metadata: pd.DataFrame, mapping_labels: dict) -> pd.DataFrame:

    # Dictionnaire pour stocker le nombre de points par label pour chaque image
    labels_count = {}

    # Parcourir les fichiers CPCE pour extraire les labels et les points
    for fichier in cpce_folder.iterdir():
        if not fichier.suffix == ".cpc": continue
            
        # Lire le fichier .cpc
        label_points = {}
        with open(fichier, 'r', encoding='latin-1') as file:
            for row in file:
                if 'Notes' not in row: continue
                label = row.replace("\n", "").split('","')[1]
                if label not in label_points:
                    label_points[label] = 0
                label_points[label] += 1

        # Mettre à jour le dictionnaire avec le nombre de points pour chaque label
        labels_count[fichier.name] = label_points

    # Extract all unique labels from the dictionary
    all_labels = set(label for counts in labels_count.values() for label in counts)
    label_dict_jpg = {key.replace('.cpc', '.JPG'): value for key, value in labels_count.items()}

    # # Initialize new columns for labels with default value 0
    df_metadata["Nb_Points"] = df_metadata.apply(lambda x: sum(list(label_dict_jpg[x['OriginalFileName']].values())) , axis=1)
    for label in sorted([mapping_labels[l] for l in all_labels]):
        df_metadata[label] = 0

    # Populate the label counts into metadata_df
    for idx, row in df_metadata.iterrows():
        image_name = row["OriginalFileName"]
        if image_name in label_dict_jpg:
            for label, count in label_dict_jpg[image_name].items():
                df_metadata.at[idx, mapping_labels[label]] = count  # Assign count to correct column
    
    return df_metadata

def get_code_benthic(code_benthic_filepath: Path) -> dict:

    if not code_benthic_filepath.exists() or not code_benthic_filepath.is_file():
        print(f"{code_benthic_filepath} not found")
        return {}

    codes = {}
    with open(code_benthic_filepath) as file:
        for i, row in enumerate(file):
            if i < 15: continue # Avoid header
            if "Notes" in row: break # Break on footer
            row = row.replace("\n", "").replace('"', '').split(',')
            codes[row[0]] = row[1]

    return codes