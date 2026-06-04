from manim import *
from manim.camera.camera import Camera
from PIL import Image
import numpy as np


def clip_image_to_mobject(image: ImageMobject, mobj: Mobject) -> ImageMobject:
    """
    Clip an ImageMobject by a mobject mask in a way that is independent
    of the scene render quality.
    """
    source = Image.fromarray(image.get_pixel_array()).convert("RGBA")
    img_w, img_h = source.size

    mask_mobj = mobj.copy()

    cam = Camera(
        pixel_width=img_w,
        pixel_height=img_h,
        frame_width=image.width,
        frame_height=image.height,
        frame_center=image.get_center(),
        background_color=BLACK,
        background_opacity=0,
    )
    cam.reset()

    mask_mobj.set_fill(WHITE, opacity=1)
    mask_mobj.set_stroke(width=0, opacity=0)

    cam.capture_mobjects([mask_mobj])
    mask = Image.fromarray(cam.pixel_array).convert("L")

    result = Image.new("RGBA", source.size, (0, 0, 0, 0))
    result.paste(source, (0, 0), mask)

    bbox = result.getbbox()
    if bbox is not None:
        result = result.crop(bbox)

    clipped = ImageMobject(result)

    clipped.move_to(mask_mobj.get_center())
    clipped.set(width=result.size[0] * image.width / img_w)

    return clipped
