from PIL import Image # Used this library to get pixel values
import os
import sys
import argparse
import hashlib

# Change here to set the number of bits to be considered from each image
a = 6 # carrier image significant bits
b = 2 # image to be embedded

def integerToBinary(rgbValue):
    r, g, b, v = rgbValue
    return ('{0:08b}'.format(r),
            '{0:08b}'.format(g),
            '{0:08b}'.format(b))

def binaryToInteger(rgbValue):
    r, g, b = rgbValue
    return (int(r, 2),
            int(g, 2),
            int(b, 2))


def mergeRGB(rgbValue1,rgbValue2):
    r1,g1,b1 = rgbValue1
    r2,g2,b2 = rgbValue2
    rgb = (r1[:a] + r2[:b],
            g1[:a] + g2[:b],
            b1[:a] + b2[:b])
    return rgb


def merge(img2, img1):

    # Check the images dimensions
    if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
        raise ValueError('Image 2 should not be larger than Image 1!')

    pixel_map1 = img1.load()
    pixel_map2 = img2.load()

    new_image = Image.new(img1.mode, img1.size)
    pixels_new = new_image.load()

    for i in range(img1.size[0]):
        for j in range(img1.size[1]):
            rgb1 = integerToBinary(pixel_map1[i, j])
            rgb2 = integerToBinary((0, 0, 0, 255))
            if i < img2.size[0] and j < img2.size[1]:
                rgb2 = integerToBinary(pixel_map2[i, j])

            rgb = mergeRGB(rgb1, rgb2)

            pixels_new[i, j] = binaryToInteger(rgb)

    return new_image

def unmerge(img):
    pixel_map = img.load()

    new_image = Image.new(img.mode, img.size)
    pixels_new = new_image.load()

    original_size = img.size

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            r, g, b = integerToBinary(pixel_map[i, j])

            rgb = (r[a:] + '000000',
                    g[a:] + '000000',
                    b[a:] + '000000')

            pixels_new[i, j] = binaryToInteger(rgb)

            if pixels_new[i, j] != (0, 0, 0):
                original_size = (i + 1, j + 1)

    new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

    return new_image

def getHash(filename):
    return hashlib.md5(open(filename, 'rb').read()).hexdigest()

def embedFile(img1, img2, outputImg):
    inputFile1 = returnPath(img1)
    inputFile2 = returnPath(img2)
    outputFile = returnPath(outputImg)
    output = merge(Image.open(inputFile1), Image.open(inputFile2))
    output.save(outputFile)
    print("Embedded")
    print("Embed Image File Size: ",os.path.getsize(inputFile1),"\t",getHash(inputFile1))
    print("Carrier File Size: ",os.path.getsize(inputFile2),"\t",getHash(inputFile2))
    print("Output File Size: ",os.path.getsize(outputFile),"\t", getHash(outputFile))


def extractFile(img, outputImg):
    inputFile = returnPath(img)
    outputFile = returnPath(outputImg)
    output = unmerge(Image.open(inputFile))
    output.save(returnPath(outputFile))
    print("Extracted.")
    print("Input File Size: ",os.path.getsize(inputFile),"\t",getHash(inputFile))
    print("Output File Size: ",os.path.getsize(outputFile),"\t",getHash(outputFile))


def returnPath(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e","--embed",help="Image to be embedded")
    parser.add_argument("-x","--extract",help="File to be extracted")
    parser.add_argument("-c","--carrier",help="Carrier Image")
    parser.add_argument("-o","--output",help="Filename for the output")

    args = parser.parse_args()
    
    if args.embed and args.carrier and args.output:
        embedFile(args.embed,args.carrier,args.output)
    elif args.extract and args.output:
        extractFile(args.extract,args.output)
    else:
        parser.print_help()
        print("\n\nEmbed: python3 steg.py -e image1 -c image2 -o output.jpg")
        print("Extract: python3 steg.py -x embeddedImage -o output.jpg\n\n")