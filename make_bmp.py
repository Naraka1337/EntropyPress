import struct

width, height = 64, 64
pixels = []
for y in range(height):
    for x in range(width):
        # Create blocks of 8x8 solid colors
        if (x // 16 + y // 16) % 2 == 0:
            pixels.append(bytes((255, 0, 0))) # Red
        else:
            pixels.append(bytes((0, 0, 255))) # Blue

filesize = 54 + 3 * width * height
bmp_header = struct.pack('<2sIHHI', b'BM', filesize, 0, 0, 54)
dib_header = struct.pack('<IiiHHIIIIII', 40, width, height, 1, 24, 0, 3*width*height, 2835, 2835, 0, 0)

with open('datasets/image.bmp', 'wb') as f:
    f.write(bmp_header)
    f.write(dib_header)
    pad = (4 - (width * 3) % 4) % 4
    
    idx = 0
    for y in range(height):
        for x in range(width):
            f.write(pixels[idx])
            idx += 1
        f.write(b'\x00' * pad)
