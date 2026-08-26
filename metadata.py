from PIL import Image

img = Image.open("test2.png")

print(img.format, img.size, img.mode)

exif_data = img.getexif()

# Display EXIF tags and values
for tag_id, value in exif_data.items():
    tag_name = Image.ExifTags.TAGS.get(tag_id, tag_id)
    print(tag_name, ":", value)