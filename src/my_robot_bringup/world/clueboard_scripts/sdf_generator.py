import os
import numpy as np
import cv2

from PIL import Image, ImageFont, ImageDraw

def sdf_generator(output_dir, num_signs):
    clueboard_banner = []
    banner = cv2.imread('clue_banner.png')

    text = [["size", "3"],
            ["crime", "3"],
            ["place", "3"],
            ["weapon", "3"],
            ["victim", "3"],
            ["time", "3"],
            ["motive", "3"],
            ["bandit", "3"]]

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

        clueboard_banner.append(populated_banner)

    # 