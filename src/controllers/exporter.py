
import json
from collections import Counter

from OpenGL.GL import GL_RGBA, GL_UNSIGNED_BYTE, glReadPixels
from PIL import Image


def count_tiles(placed_tiles):
    """
    Retourneer Counter: { tile_name: aantal }.
    """
    print(type(placed_tiles[0]))
    names = [t['tile'].name for t in placed_tiles]
    return Counter(names)

def capture_topdown(width, height, filename="dungeon_map.png"):
    """
    Lees de hele buffer uit (RGBA), flip vertically en sla op als PNG.
    """
    data = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)
    img = Image.frombytes("RGBA", (width, height), data)
    # OpenGL is bottom-up, dus we flippen
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(filename)
    return filename