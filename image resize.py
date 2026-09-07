from PIL import Image, ImageFilter
import os

# ==================================================
# SETTINGS
# ==================================================

TARGET_WIDTH = 832
TARGET_HEIGHT = 551

input_image = r"C:\Users\This PC\Pictures\blog images\upload code.png"

# White detection settings
WHITE_THRESHOLD = 245
WHITE_PERCENTAGE = 0.95


# ==================================================
# OPEN IMAGE
# ==================================================

try:
    image = Image.open(input_image).convert("RGB")

    print("Original size:", image.size)

except Exception as e:
    print("Error opening image:")
    print(e)
    input("Press Enter to exit...")
    exit()


# ==================================================
# REMOVE TOP WHITE BORDER
# ==================================================

width, height = image.size


def is_white_row(y):

    white_pixels = 0

    for x in range(width):

        r, g, b = image.getpixel((x, y))

        if (
            r >= WHITE_THRESHOLD
            and g >= WHITE_THRESHOLD
            and b >= WHITE_THRESHOLD
        ):
            white_pixels += 1

    return (white_pixels / width) >= WHITE_PERCENTAGE


top = 0

while top < height and is_white_row(top):
    top += 1


# ==================================================
# REMOVE BOTTOM WHITE BORDER
# ==================================================

bottom = height - 1

while bottom >= 0 and is_white_row(bottom):
    bottom -= 1


# ==================================================
# CROP ONLY TOP AND BOTTOM
# ==================================================

if top < bottom:

    image = image.crop(
        (
            0,
            top,
            width,
            bottom + 1
        )
    )

    print("Top white border removed:", top, "pixels")
    print("Bottom white border removed:",
          height - 1 - bottom, "pixels")

else:

    print("No white borders detected.")


print("After border removal:", image.size)


# ==================================================
# RESIZE FULL IMAGE
# ==================================================

image_ratio = image.width / image.height

target_ratio = TARGET_WIDTH / TARGET_HEIGHT


if image_ratio > target_ratio:

    # Image is wider
    new_width = TARGET_WIDTH

    new_height = round(
        TARGET_WIDTH / image_ratio
    )

else:

    # Image is taller
    new_height = TARGET_HEIGHT

    new_width = round(
        TARGET_HEIGHT * image_ratio
    )


resized = image.resize(
    (new_width, new_height),
    Image.Resampling.LANCZOS
)


# ==================================================
# CREATE 832 × 551 CANVAS
# ==================================================

# Use white background
final_image = Image.new(
    "RGB",
    (TARGET_WIDTH, TARGET_HEIGHT),
    (255, 255, 255)
)


# ==================================================
# CENTER IMAGE
# ==================================================

left = (TARGET_WIDTH - new_width) // 2
top = (TARGET_HEIGHT - new_height) // 2


final_image.paste(
    resized,
    (left, top)
)


# ==================================================
# SHARPEN THE IMAGE
# ==================================================

# Important for small Arduino text
final_image = final_image.filter(
    ImageFilter.UnsharpMask(
        radius=1.2,
        percent=150,
        threshold=2
    )
)


# ==================================================
# SAVE AS PNG
# ==================================================

folder = os.path.dirname(input_image)

filename = os.path.splitext(
    os.path.basename(input_image)
)[0]


output_image = os.path.join(
    folder,
    filename + "_Instructables_832x551.png"
)


final_image.save(
    output_image,
    "PNG",
    optimize=True
)


# ==================================================
# RESULT
# ==================================================

print()
print("==========================================")
print("       IMAGE PROCESSING COMPLETED")
print("==========================================")
print()

print("Original Size       :", (width, height))
print("After Border Removal:", image.size)
print("Final Size          :", final_image.size)

print()
print("Output:")
print(output_image)

print()
print("Format: PNG")
print("Sharpening: Enabled")
print("Cropping: None")
print("Distortion: None")

print()
print("==========================================")

input("Press Enter to exit...")
