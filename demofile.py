import os
from io import StringIO
import pandas as pd
import requests
from tabulate import tabulate
from requests.compat import urljoin as urlj
import json
from IPython.display import Image, display
import cv2
import ast
import gradio as gr
from PIL import Image
import os
import requests


API_TOKEN_FROM_YOUR_PROFILE = '0953ed57513ab57a7dccbc6859472657383dd56b'
token = API_TOKEN_FROM_YOUR_PROFILE

def request_data(url):
    auth_header = {"Authorization": f"Token {token}"}


    r = requests.get(url, headers=auth_header)
    req = json.loads(r.text)
    return req

projects_url = "https://sweden.trapper-project.org/media_classification/api/projects"
projects = request_data(projects_url)

p13_df = pd.read_csv('observations_0_13.csv')
p6_df = pd.read_csv('observations_0_6.csv')
p2_df = pd.read_csv('observations_0_2.csv')

def display_image(file_path, width=1000, height=None):
    print(file_path)
    if os.path.exists(file_path):
        display(Image(file_path, width=width, height=height))
    else:
        print('File not in dir (yet)')

def draw_bboxs(img_path, coordinates, out_path=None, display_now=False):
    image = cv2.imread(img_path)
    height, width, channels = image.shape
    for c in coordinates:
        start_point = (int(c[0]*width), int(c[1]*height))
        #end_point = (int(c[2]*width), int(c[3]*height))
        end_point = (int(c[0]*width)+ int(c[2]*width), int(c[1]*height) + int(c[3]*height))
        cv2.rectangle(image, start_point, end_point, color=(0,255,0), thickness=2)
    if not out_path:
        out_path = img_path.replace('.', '_bboxes.')
   
    cv2.imwrite(out_path, image)

    if display_now:
        display_image(out_path)
    return out_path

def select_by_species(df, species):
    return df[df['commonName'] == species]

def show_random_species(df, species):
    display_now = True
    sdf = select_by_species(df, species)
    if sdf.empty:
        print('Species not in available photo set')
    row = sdf.sample(n=None)
    print(row.to_markdown())
    row = row.squeeze()
    photo_path = download_image_url(row.filePath, f'{row.fileName}.png', display_now=display_now)
    row['local_path'] = photo_path
    row['bboxes'] = ast.literal_eval(row['bboxes'])
    return row

def download_image_url(url, file_name, file_path='photos', display_now=False):
    photo_path = os.path.join(file_path, file_name)
    auth_header = {"Authorization": f"Token {token}"}
    r = requests.get(url, headers=auth_header)

    if r.status_code == 200:
        os.makedirs(file_path, exist_ok=True)
        with open(photo_path, 'wb') as out_file:
            out_file.write(r.content)
    else:
        print(f"ERROR code: {r.status_code} on URL: {url}")
        return None
    
    if display_now:
        display_image(photo_path)
    
    return photo_path

def display_image(photo_path):
    image = Image.open(photo_path)
    image.show()
    return image

def outputImg(df_name, species):
    print("df_name", df_name)
    if df_name == "p13_df":
        df = p13_df
    elif df_name == "p6_df":
        df = p6_df
    elif df_name == "p2_df":
        df = p2_df
    else:
        print("Invalid DataFrame selected")
        return None
    image_info = show_random_species(df, species)
    print(image_info['local_path'], image_info.to_string())
    details_table = tabulate(pd.DataFrame(image_info).transpose(), headers='keys', tablefmt='pipe')
    print("details_table",details_table)
    bbimg = draw_bboxs(image_info['local_path'], image_info.bboxes)#image_info['local_path'], image_info.to_string()
    return display_image(bbimg), details_table#image_info.to_string()

iface = gr.Interface(
    fn=outputImg,
    inputs=[
        gr.inputs.Dropdown(label="df", choices=["p13_df", "p6_df", "p2_df"]),
        gr.inputs.Dropdown(label="species", choices=list(pd.concat([p13_df['commonName'], p6_df['commonName'], p2_df['commonName']]).unique())),
        #gr.inputs.Textbox(label="DataFrame")
    ],
    outputs=[
        gr.outputs.Image(type="pil", label="Random Image"),
        gr.outputs.Textbox(label="Details", type="text")
    ]
)

iface.launch()
