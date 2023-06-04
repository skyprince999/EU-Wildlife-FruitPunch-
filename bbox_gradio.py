import gradio as gr
import pandas as pd
import cv2
import ast
import numpy as np
from PIL import Image, ImageDraw, ImageFont

df = pd.read_excel("C:\\Users\\AVANISH SINGH\\Downloads\\sample_df.xlsx")
print(df)

def process_image(image_name, confidence):
    row = df[df['filename_gs'] == image_name]
    bbox_str = row['bbox'].values[0]
    bbox = ast.literal_eval(bbox_str)
    confidence_value = row['conf'].values[0]
    common_name = row['common_name'].values[0]
    image_path = 'treshold_data_bbox\\' + image_name
    image = Image.open(image_path)
    x, y, w, h = [round(float(coord) * image.width) for coord in bbox]
    draw = ImageDraw.Draw(image)
    draw.rectangle([(x, y-h), (x+w, y+h)], outline=(0, 255, 0), width=5)#(x+w, y + h)
    
    text = f"{common_name} : {confidence_value:.3f}"
    print("Common Name",text)
    bbox = draw.textbbox((x,y-h-50), text, font=ImageFont.truetype("Roboto-BoldItalic.ttf",35))
    draw.rectangle(bbox, fill="red")
    draw.text((x, y-h-50), text, fill="#FFFFFF", font=ImageFont.truetype("Roboto-BoldItalic.ttf", 30))#"C:\Users\AVANISH SINGH\Anaconda3\Lib\site-packages\geemap\data\fonts\arial.ttf"
    
    #text = f"Confidence: {confidence_value:.3f}"
    #print("Confidence",text)
    #draw.text((100, 300), text, fill="#808000", font=ImageFont.truetype("Roboto-BoldItalic.ttf", 50))
    
    confidence_mask = confidence_value >= float(confidence)
    if not confidence_mask:
        image = Image.fromarray(np.zeros((image.height, image.width, 3), dtype=np.uint8))

    #image.save("output_bbox.png")
    return np.array(image)#, common_name


image_names = df['filename_gs'].unique().tolist()
confidence_slider = gr.inputs.Slider(minimum=0, maximum=1, default=0.5, label="Select Confidence")
inputs = gr.inputs.Dropdown(choices=image_names, label="Select an image")
outputs = gr.outputs.Image(type="numpy", label="Image with bounding boxes and confidence")
app = gr.Interface(fn=process_image, inputs=[inputs, confidence_slider], outputs=outputs)

app.launch()