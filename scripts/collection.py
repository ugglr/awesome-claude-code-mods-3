#!/usr/bin/env python3
"""Make a contact sheet without cropping any individual screenshot."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
names=['context-meter','staged-review','task-board','regex-lab','focus-clock','file-tree']
canvas=Image.new('RGB',(1500,1040),'#080d16')
for i,name in enumerate(names):
 image=Image.open(ROOT/'assets/screenshots'/f'{name}.png').convert('RGB')
 image.thumbnail((475,490),Image.Resampling.LANCZOS)
 x=15+(i%3)*495;y=15+(i//3)*510
 canvas.paste(image,(x,y))
canvas.save(ROOT/'assets/screenshots/collection.png')
print('Built six-preview collection image without cropping')
