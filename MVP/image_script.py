import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import urllib.request
import requests
import random
import json
import os

# PIL Loader Issue Workaround
def register_extension(id, extension): Image.EXTENSION[extension.lower()] = id.upper()
Image.register_extension = register_extension
def register_extensions(id, extensions):
  for extension in extensions: register_extension(id, extension)
Image.register_extensions = register_extensions


# API Key and URL
KEY = os.environ['PIXABAY_KEY']

URL = "https://pixabay.com/api/?key="

# Image Generator Helper Functions
def prep_query_string(q="", category="", image_type="all", per_page=40):
    queries = {"&q=": q.replace(" ","+"), "&category=": category.replace(" ", "+"), "&image_type=": image_type.replace(" ", "+"), "&per_page=": str(per_page)}
    return queries

def pull_images(q="",category="",image_type="all", per_page=40):
    api_call = URL + KEY
    queries = prep_query_string(q, category, image_type, per_page)
    for query in queries:
        api_call += (query + queries[query])
        print(api_call)
    api_call = requests.get(api_call)
    return json.loads(api_call.text)

def resize_logo(logo, basewidth):
    logo_w, logo_h = logo.size
    logo_wpercent = (basewidth / float(logo_w))
    logo_hsize = int((float(logo_h) * float(logo_wpercent)))
    logo = logo.resize((basewidth, logo_hsize), Image.ANTIALIAS)
    return logo

def get_boxes(image_w, image_h, logo_w, logo_h):
    top_right = (image_w - (image_w // 3), image_h // 10)
    top_left = (image_w // 10, image_h // 10)
    bottom_right = (image_w - (image_w // 3), image_h - (image_h // 8))
    bottom_left = (image_w // 10, image_h - (image_h // 8))
    center = ((image_w // 2) - (logo_w // 2), (image_h // 2) - (logo_h // 2))
    return top_right, top_left, bottom_right, bottom_left, center

def create_image(image, logo_path):
    # Reading image and logo first
    image = Image.open(image)
    logo = Image.open(logo_path)
    # Getting image size
    image_w, image_h = image.size
    # Resizing Logo as needed:
    basewidth = image_w // 4
    logo = resize_logo(logo, basewidth)
    # Targeting image area
    box = (image_w - (image_w // 3), image_h // 10)
    # Creating mask to paste without weird background
    logo_mask = logo.convert("RGBA")
    # Pasting
    image.paste(logo, box, logo_mask)
    return image


# Image Generator Function
def generate_image(search_term="", category="", image_type="all", logo_path='../Image_Gen/test_logo.png'):
    # Loading json results
    images_json = pull_images(search_term, category, image_type)
    # Selecting image randomly from json response:
    rand_image = random.choice(images_json['hits'])
    # Reading Image
    image = urllib.request.urlopen(rand_image['largeImageURL'])
    # Creating Final Result
    final = create_image(image, logo_path)
    plt.imshow(final)
    final.save('image_test.jpg')
    return final

# Generate Multiple Images
def generate_images(search_term="", category="", image_type="all", logo_path="./test_logo.png", num_images=10):
    #Loading json results
    images_json = pull_images(search_term, category, image_type)
    
    # Creating list of randomly chosen images
    rand_images = []
    while len(rand_images) != num_images:
        rand_image = random.choice(images_json['hits'])
        image_url = rand_image['largeImageURL']
        rand_image = urllib.request.urlopen(rand_image['largeImageURL'])
        rand_image = Image.open(rand_image)
        rand_images.append({'image': rand_image, 'url': image_url})
    
    return rand_images      