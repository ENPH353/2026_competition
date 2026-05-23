import numpy as np
import cv2
import shutil
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw

def quick_clear(path, file_type):
    
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
        

def banner_generator(script_dir, num_signs):
    output_path = script_dir.parent / 'models' / 'clue_board' / 'banners'
    base_banner_path = script_dir.parent / "clueboard_scripts" / "clue_banner.png"
    
    quick_clear(output_path, ".jpg")

    banner_paths_array = []

    banner = cv2.imread(base_banner_path.as_posix())

    text = [["SIZE", "3"],
            ["CRIME", "3"],
            ["PLACE", "3"],
            ["WEAPON", "3"],
            ["VICTIM", "3"],
            ["TIME", "3"],
            ["MOTIVE", "3"],
            ["BANDIT", "3"]]

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