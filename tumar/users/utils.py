from io import BytesIO
from PIL import Image
from django.core.files import File


def reorient_image(im):
    try:
        image_exif = im._getexif()
        image_orientation = image_exif[274]
        if image_orientation in (2, "2"):
            return im.transpose(Image.FLIP_LEFT_RIGHT)
        elif image_orientation in (3, "3"):
            return im.transpose(Image.ROTATE_180)
        elif image_orientation in (4, "4"):
            return im.transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (5, "5"):
            return im.transpose(Image.ROTATE_90).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (6, "6"):
            return im.transpose(Image.ROTATE_270)
        elif image_orientation in (7, "7"):
            return im.transpose(Image.ROTATE_270).transpose(Image.FLIP_TOP_BOTTOM)
        elif image_orientation in (8, "8"):
            return im.transpose(Image.ROTATE_90)
        else:
            return im
    except (KeyError, AttributeError, TypeError, IndexError):
        return im


def compress(image):
    if image.size < 600000:
        return image

    new_image = None
    im = Image.open(image)

    if im.format != "PNG":
        # Reorient image to preserve right orientation
        im = reorient_image(im)

        if im.mode != "RGB":
            im = im.convert("RGB")

        # create a BytesIO object
        im_io = BytesIO()

        # save image to BytesIO object
        im.save(im_io, "JPEG", quality=70)

        # create a django-friendly Files object
        new_image = File(im_io, name=image.name)
    else:
        # Reorient image to preserve right orientation
        im = reorient_image(im)

        # create a BytesIO object
        im_io = BytesIO()

        im = im.resize((im.size[0] // 2, im.size[1] // 2))

        # save image to BytesIO object
        im.save(im_io, "PNG", optimize=True, quality=70)

        # create a django-friendly Files object
        new_image = File(im_io, name=image.name)

    if new_image:
        return new_image
    return image
