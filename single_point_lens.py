import numpy as np
import pygame
from PIL import Image

FILENAME = ['images/galaxy.png', 'images/circle.png', 'images/odysseus.jpg', 'images/circle2.png'][1]
W,H = 1500, 900

pygame.init()
screen = pygame.display.set_mode([W, H])

pygame.display.set_caption("Single point lens")

# scale parameter such that Einstein radius = 1
SCALE = min(W,H)/3

# coordinate conversion stuff
def polar2xy(r, theta):
    return r * np.cos(theta), r * np.sin(theta)
def xy2polar(x, y):
    return np.sqrt(x**2 + y**2), np.arctan2(y, x)

def xy2pygame(x,y):
    return x*SCALE + W/2, H/2 - y*SCALE
def pygame2xy(x,y):
    return (x-W/2)/SCALE, -(y-H/2)/SCALE

def polar2pygame(r, theta):
    return xy2pygame(*polar2xy(r,theta))
def pygame2polar(x,y):
    return xy2polar(*pygame2xy(x,y))

ORIGIN = xy2pygame(0,0)

# Object - source or image
class Object():
    # all coordinates are in 'pygame' type
    def __init__(self, x, y, colors_rgba):
        self.reference_x = np.array(x)
        self.reference_y = np.array(y)
        
        self.colors = np.array(colors_rgba)

        # remove unnecessary points with alpha = 0
        mask_alpha = self.colors[:,3] > 0
        self.colors = self.colors[mask_alpha]
        self.reference_x = self.reference_x[mask_alpha]
        self.reference_y = self.reference_y[mask_alpha]

        self.x = self.reference_x
        self.y = self.reference_y

    def recenter(self, cx, cy):
        self.x = self.reference_x + cx - ORIGIN[0]
        self.y = self.reference_y + cy - ORIGIN[1]

    def draw(self, surface):
        pixels = pygame.surfarray.pixels3d(surface)
        pixels_alpha = pygame.surfarray.pixels_alpha(surface)[:, :, np.newaxis]

        points = np.int64(np.stack((self.x, self.y), axis=1))   

        mask = (points[:,0] >= 0) & (points[:,0] < W) & (points[:,1] >= 0) & (points[:,1] < H)
        points = points[mask]
        colors_rgba = self.colors[mask]

        pixels[points[:,0], points[:,1]] = colors_rgba[:,:3]
        pixels_alpha[points[:,0], points[:,1]] = colors_rgba[:,3].reshape(-1,1)
 

def lens(obj):
    r, theta = pygame2polar(obj.x, obj.y)
    r1 = r/2 + np.sqrt(r**2/4 + 1)
    r2 = r/2 - np.sqrt(r**2/4 + 1)
    im1 = Object(*polar2pygame(r1, theta), obj.colors)
    im2 = Object(*polar2pygame(r2, theta), obj.colors)
    return im1, im2

def img2source(filename, size=0.2):
    # size is in 'xy' type coordinates
    image = Image.open(filename).convert('RGBA')
    ratio = image.height/image.width
    
    magic_number = 700
    if image.width > image.height:
        im_w = min(magic_number, image.width)
        im_h = int(im_w*ratio)
    else:
        im_h = min(magic_number, image.height)
        im_w = int(im_h/ratio)
    image = image.resize((im_w, im_h))

    print(image.size)

    image_array = np.array(image)

    x_image = np.tile(np.linspace(-size, size, im_w), im_h)
    y_image = np.repeat(np.linspace(size*ratio, -size*ratio, im_h), im_w)
    x_image, y_image = xy2pygame(x_image, y_image)

    colors = image_array.reshape(-1,4)

    return Object(x_image, y_image, colors)



source = img2source(FILENAME, 0.3)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0]:
        source.recenter(*pygame.mouse.get_pos())

    surface = pygame.Surface((W, H), pygame.SRCALPHA)
    surface.fill((0,0,0,0))
    
    screen.fill("black")

    im1, im2 = lens(source)
    source.draw(surface)
    im1.draw(surface)
    im2.draw(surface)

    pygame.draw.circle(surface, "white", xy2pygame(0, 0), SCALE, 2)
    pygame.draw.circle(surface, "white", xy2pygame(0, 0), 3)
    
    screen.blit(surface, (0,0))
    pygame.display.flip()

pygame.quit()