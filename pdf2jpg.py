"""This is the routine that will actually strip images out of a pdf

NB: PyPDF2 only works in python 2"""

import PyPDF2
from PIL import Image
import os,sys,getopt
from kmtshi.base_directories import base_static_image,jpeg_path

def pdf2jpg(input_pdf, output_dir):
    """
    :param input_pdf: This is the pdf which images will be extracted
    :param output_dir: This is the directory to which the images will be saved

    """
    input1 = PyPDF2.PdfFileReader(open(input_pdf, "rb"))
    page0 = input1.getPage(0)
    xObject = page0['/Resources']['/XObject'].getObject()

    for obj in xObject:
        if xObject[obj]['/Subtype'] == '/Image':
            size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
            data = xObject[obj].getData()
            if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                mode = "RGB"
            else:
                mode = "P"

            ## Set-up what the output filenames should be based on obj name
            if obj[1:] == 'R8':
                obj_name = '.B-Filter-SOURCE'
            elif obj[1:] == 'R9':
                obj_name = '.REF'
            elif obj[1:] == 'R10':
                obj_name = '.SOURCE-REF-MMM-mag'
            elif obj[1:] == 'R11':
                obj_name = '.B.DATE'
            elif obj[1:] == 'R12':
                obj_name = '.V.DATE'
            elif obj[1:] == 'R13':
                obj_name = '.I.DATE'

            # Write out to appropriate directory:
            if xObject[obj]['/Filter'] == '/FlateDecode':
                img = Image.frombytes(mode, size, data)
                img.save(output_dir + obj_name + ".png")

                # Issue call to command line to convert
                convert_cmmd = 'convert '+output_dir+obj_name+'.png '+output_dir+obj_name+'.jpeg'
                os.system(convert_cmmd)

                # Issue call to remove first version:
                rm_cmmd = 'rm -f '+output_dir+obj_name+'.png'
                os.system(rm_cmmd)

            elif xObject[obj]['/Filter'] == '/DCTDecode':
                img = open(output_dir + obj_name + ".jpeg", "wb")
                img.write(data)
                img.close()
            elif xObject[obj]['/Filter'] == '/JPXDecode':
                img = open(output_dir + obj_name + ".jp2", "wb")
                img.write(data)
                img.close()

                # Issue call to command line to convert
                convert_cmmd = 'convert ' + output_dir + obj_name + '.jp2 ' + output_dir + obj_name + '.jpeg'
                os.system(convert_cmmd)

                # Issue call to remove first version:
                rm_cmmd = 'rm -f ' + output_dir + obj_name + '.jp2'
                os.system(rm_cmmd)

            # Figure out the flipping. Will it overwrite? Yep!
            file = output_dir + obj_name + '.jpeg'
            obj2 = Image.open(file)
            rot = obj2.transpose(Image.FLIP_TOP_BOTTOM)
            rot.save(file)

    txt_out = 'Success! Probabaly...'
    return txt_out

def main(argv):
    pdf = 'temp.pdf'
    try:
        opts, args = getopt.getopt(argv,"p:",["pdf="])
    except getopt.GetoptError:
        print('pdf2jpg.py -p <pdf name as string>')
        print('--pdf also permitted')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p","--pdf"):
            pdf = arg
    if pdf == 'temp.pdf':
        print('You must specify the pdf')
        print('pdf2jpg.py -p <pdf name as string>')
        sys.exit(2)


    # I now have the name of the pdf. The assumption of this is that it is the full path to the google directory.
    # Therefore, I need to deconstruct that and figure out the output where it should be saved within the /static area

    file = pdf.split('/')[-1]
    base_folder = jpeg_path(file,static=True,folder_only=True)
    base_input = jpeg_path(file,static=True)

    # Make sure that the static folder exists
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    # Strip the pdf and put the jpegs in that folder
    pdf2jpg(pdf,base_input)


if __name__ == "__main__":
    main(sys.argv[1:])

