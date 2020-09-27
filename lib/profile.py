from PIL import Image


def crop_resize_image(im, new_size=(500, 500)):
    w, h = im.size
    if w == h:
        im_resize = im.resize(new_size)
    elif w > h:
        offset = (w - h) // 2
        lu = (offset, 0)
        rd = (offset + h, h)
        im_crop = im.crop((*lu, *rd))
        im_resize = im_crop.resize(new_size)
    elif w < h:
        offset = (h - w) // 2
        lu = (0, offset)
        rd = (w, offset + w)
        im_crop = im.crop((*lu, *rd))
        im_resize = im_crop.resize(new_size)
    return im_resize