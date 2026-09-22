#!/usr/bin/env python3
"""Prep a photo for ASCII conversion: strip the background, boost local
contrast, and composite onto pure white so the background maps to the
blank end of the ASCII ramp.
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

# u2net is the small, general-purpose model (~176 MB) -- rembg's own default
# ("birefnet-general"/"bria-rmbg") is a >1 GB model that's overkill here.
SESSION = new_session("u2net")


def prep_photo(input_path: str, output_path: str = "source-prepped.png") -> None:
    src = Image.open(input_path).convert("RGBA")

    cutout = remove(src, session=SESSION)

    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    white_bg.alpha_composite(cutout)
    rgb = white_bg.convert("RGB")

    gray = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)

    Image.fromarray(boosted).save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: prep_photo.py <input-image> [output-png]")
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(sys.argv[1], out)
