# This is the main script where everything comes together

# Import Dependencies & Scripts
import text_script as txtscript
import image_script as imscript

from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
  import Features, EmotionOptions, EntitiesOptions, KeywordsOptions

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageDraw, ImageFont
import urllib.request
import subprocess
import requests
import random
import json
import os

# NLU API INFO
natural_language_understanding = NaturalLanguageUnderstandingV1(
  username=os.environ['IBM_USER'],
  password=os.environ['IBM_PASS'],
  version='2018-03-16')


# Draw Text Function (To write slogan)
def draw_text(text, size, fill=None):
    font = ImageFont.truetype(
        '~/Library/Fonts/Helvetica', size
    )
    size = font.getsize(text) # Returns the width and height of the given text, as a 2-tuple.
    im = Image.new('RGBA', size, (0, 0, 0, 0)) # Create a blank image with the given size
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), text, font=font, fill=fill) #Draw text
    return im


# Mockup Generator
def generate_mockups(description='', num_samples=10, predict_len=20, temperature=0.6, size=30, fill=(82,124, 178), logo_path='./test_logo.png'):
    # Loading needed components
    main_images = imscript.generate_images(description, num_images=num_samples)
    slogans = txtscript.get_candidates(num_samples, predict_len, temperature)
    logo = Image.open(logo_path)

    # Looping through each main image JSON
    for image_data in main_images:
        # Getting Image and URL
        image, image_url = image_data['image'], image_data['url']
        # Getting sizes of images
        image_w, image_h = image.size
        logo_w, logo_h = logo.size

        # Saving slogan text for analysis later
        slogan_txt = slogans[main_images.index(image_data)]
        image_data['slogan'] = slogan_txt
        # Creating Slogan Image to load on main image
        slogan = slogans[main_images.index(image_data)]
        slogan = draw_text(slogan, (image_h // 16), fill)

        # Adjusting size of logo
        if logo_h >= logo_w:
            basewidth = image_w // 10
        else:
            basewidth = image_w // 4

        # Resized logo with new dimensions, and logomask
        new_logo = imscript.resize_logo(logo, basewidth)
        logo_w , logo_h = new_logo.size
        logo_mask = new_logo.convert("RGBA")

        # Getting Box Coordinates
        top_right, top_left, bottom_right, bottom_left, center = imscript.get_boxes(image_w, image_h, logo_w, logo_w)
        boxes = [top_right, top_left, bottom_right, bottom_left, center]

        # Setting Box Coordinates for logo and slogan
        logo_box = random.choice(boxes)
        if logo_box == center:
            slogan_box = random.choice([top_right, top_left, bottom_right, bottom_left])
        elif logo_box == top_right or logo_box == top_left:
            slogan_box = random.choice([bottom_right, bottom_left, center])
        elif logo_box == bottom_right or logo_box == bottom_left:
            slogan_box = random.choice([top_right, top_left, center])

        # Now Pasting new_logo and slogan
        image.paste(new_logo, logo_box, logo_mask)
        image.paste(slogan, slogan_box, slogan)
    # Returning list of final mockups w/ URL
    return main_images

# Analyze Image Caption with NLU
def analyze(image_data):
    image_caption = subprocess.check_output('python captioner.py --image=' + image_data['url'], shell=True)
    # Cleaning Image Caption response:
    text = str(image_caption)
    text = text.split('>')[1]
    text = text.split('<')[0]
    print(text)
    response = natural_language_understanding.analyze(
      text=text,
      features=Features(
        emotion=EmotionOptions(),
        keywords=KeywordsOptions(
          emotion=True,
          sentiment=True,
          limit=10)))
    return response
