import csv
import cv2
import numpy as np
import requests
import shutil

from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

def quick_clear(path, file_type):
    '''
    '''
    if path.exists() and path.is_dir():
        deleted_count = 0
        
        # path.glob find all files matching the pattern (e.g., *.jpg)
        for file in path.glob(f"*{file_type}"):
            if file.is_file():  # Safety check to ensure it's a file, not a folder
                file.unlink()   # Delete the file
                deleted_count += 1
                
        print(f"Cleared {deleted_count} '{file_type}' files from: {path}")
    else:
        path.mkdir() # If no path is found, make new one
        print(f"Directory not found. Created empty folder at: {path}")


def loadCrimesProfileCompetition(script_folder_path):
    '''
    @brief returns a set of clues for one game and save them to plates.csv

    @retval clue dictionary of the form 
                [size:value, victim:value, ...
                 crime:value,time:value,
                 place:value,motive:value,
                 weapon:value,bandit:value]
    '''
    URL = "https://phas.ubc.ca/~miti/ENPH353/ENPH353Clues.csv"

    print("Loading clues ...")
    response = None
    try:
        response = requests.get(URL, timeout=2)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # This will catch HTTPError, ConnectionError, Timeout, etc.
        print(f"The request failed: {e}")

    if response is None:
        print("Could not download clues. Using default clues!")
        key_list = ["SIZE", "CRIME", "PLACE", "WEAPON", 
                    "VICTIM", "TIME", "MOTIVE", "BANDIT",]
        value_list = ["D 3", "D SPIN", "D HALLWAY", "D WHEEL",
                      "D ELECTRONS", "D BIG BANG", "D NEGATIVITY", "D PROTON"]
    else:
        raw = response.text.split('\n')
        key_list   = raw[0].split(',')
        value_list = raw[1].split(',')

    print("### CLUES USED: ")
    # We save the clues to clues.csv
    with open(script_folder_path / "clues.csv", 'w') as plates_file:
        csvwriter = csv.writer(plates_file)

        for (key, value) in zip(key_list, value_list):
            csvwriter.writerow([key, value.upper()])
            print(key.upper() + ":" + value.upper())

    #We put the clues and values in a list to be displayed on the boards
    clues = [[key.upper(), value.upper()] for key, value in zip(key_list, value_list)]

    return clues
        

def banner_generator(script_dir, num_signs):
    '''
    @brief
    '''

    # Download clues from website:

    output_path = script_dir.parent / 'models' / 'clue_board' / 'banners'
    base_banner_path = script_dir.parent / "clueboard_scripts" / "clue_banner.png"
    
    quick_clear(output_path, ".jpg")

    banner_paths_array = []

    banner = cv2.imread(base_banner_path.as_posix())

    text = loadCrimesProfileCompetition(script_dir.parent)

    # Generate the images with text
    for i in range(num_signs):
        blank_plate_pil = Image.fromarray(banner)
        draw = ImageDraw.Draw(blank_plate_pil)
        font_size = 90
        monospace = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf", font_size)

        font_color = (255,0,0)
        draw.text((250, 30), text[i][0], font_color, font=monospace)
        draw.text((30, 250), text[i][1], font_color, font=monospace)
        # Convert back to OpenCV image and save
        populated_banner = np.array(blank_plate_pil)
        
        jpg_name = f"banner_{i}.jpg"
        banner_paths_array.append("banners/" + jpg_name)
        cv2.imwrite(str(output_path / jpg_name), populated_banner)

def sdf_generator(script_dir, num_signs):
    '''
    '''
    output_path = script_dir.parent / 'models' / 'clue_board'

    quick_clear(output_path, ".sdf")

    clueboard_sdf_paths = []

    for i in range(num_signs):
        model_name = f"clueboard_{i}"

        sdf_template = f"""<?xml version="1.0"?>
<sdf version="1.8">
    <model name="{model_name}">
        <static>true</static>
        <link name="clueboard_link">
            <collision name='collision'>
                <pose>0 0 0.04 0 0 0</pose>
                <geometry>
                    <box>
                        <size>0.2 0.01 0.16</size>
                    </box>
                </geometry>
            </collision>

            <visual name='visual'>
                <geometry>
                    <box>
                        <size>0.2 0.01 0.16</size>
                    </box>
                </geometry>
                <material>
                    <ambient>0 0 1 1</ambient>
                    <diffuse>1 1 1 1</diffuse>
                    <specular>0 0.5 0 0</specular>
                    <emissive>0 0 0 1</emissive>
                </material>
            </visual>
        </link>
        <link name="banner_link">
            <pose>0 0.01 0.02 0 0 0</pose>
            <collision name="collision">
                <geometry>
                    <box>
                        <size>1e-6 1e-6 1e-6</size>
                    </box>
                </geometry>
            </collision>

            <visual name="visual">
                <geometry>
                    <box>
                        <size>0.15 1e-4 0.1</size>
                    </box>
                </geometry>
                
                <material>
                    <ambient>1 1 1 1</ambient>
                    <diffuse>1 1 1 1</diffuse>
                    <specular>0.1 0.1 0.1 1</specular>

                    <pbr>
                        <metal>
                            <albedo_map>banners/banner_{i}.jpg</albedo_map>
                        </metal>
                    </pbr>
                </material>
            </visual>
        </link>
    </model>
</sdf>
        """

        full_sdf_path = output_path / f"{model_name}.sdf"
        full_sdf_path.write_text(sdf_template)
        clueboard_sdf_paths.append(full_sdf_path.as_posix())
    
    return clueboard_sdf_paths
        

def main():
    script_dir = Path(__file__).resolve().parent
    num_signs = 8

    banner_generator(script_dir, num_signs)
    sdf_paths = sdf_generator(script_dir, num_signs)
    return sdf_paths

if __name__ == "__main__":
    main()