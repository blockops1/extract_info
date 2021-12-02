import hashlib
import os
import sys


class IterRegistry(type):
    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__"):
                yield attr


# Data structure designed to hold file information
class FoundFile(metaclass=IterRegistry):
    def __init__(self):
        # print("new FoundFile created")
        self.name = ""
        self.type = ""
        self.start = 0
        self.size = 0
        self.end = 0
        self.hash = 0
        self.header = ""
        self.trailer = ""
        self.signature = ""


# Recovers files found in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def recover_file(file_handle, found_temp):
    # set up directory to save the file to
    path = "RecoveredFiles"
    if not os.path.exists(path):
        os.makedirs(path)

    # read from section of file_handle containing the file into new file
    file_handle.seek(found_temp.start)
    output_file = open(os.path.join(path, found_temp.name), 'wb')
    output_file.write(file_handle.read(found_temp.size))
    output_file.close()

    # create sha256
    hash_file = open(os.path.join(path, found_temp.name), 'rb')
    hash_file_full = hash_file.read()
    hash_file.close()
    hash_sha256 = hashlib.sha256(hash_file_full).hexdigest()
    found_temp.hash = hash_sha256

    # display progress to user
    x = found_temp
    print("File found - name:", x.name, "type:", x.type, "start:", x.start, "end:", x.end, "size:", x.size)
    return 0


# Handles the discovery of an AVI file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def avi(file_handle, position, temp_object):
    file_handle.seek(position + 4)
    temp_object.start = position
    # read file size from byte offset
    temp_object.size = int.from_bytes(file_handle.read(4), 'little') + 8
    temp_object.name = str(temp_object.start) + ".avi"
    temp_object.end = temp_obj.start + temp_obj.size - 1
    temp_object.type = "avi"
    # recover file
    recover_file(file_handle, temp_object)
    file_handle.seek(position)
    return 0


# Handles the discovery of an JPG file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def jpg(file_handle, position, temp_object):
    temp_object.name = str(position) + ".jpg"
    temp_object.type = "jpg"
    temp_object.start = position
    position_jpg = position
    # look for file end marker
    end_position_jpg = 0
    # search for end of file
    while position_jpg < file_size:
        file_handle.seek(position_jpg)
        current_bytes = bytes.hex(file_handle.read(2))
        if current_bytes == "ffd9":
            # end of file found
            end_position_jpg = position_jpg + 1
            break
        position_jpg += 1
    temp_object.end = end_position_jpg
    temp_object.size = temp_object.end - temp_object.start + 1
    # recover file
    recover_file(file_handle, temp_object)
    return 0


# Handles the discovery of an PNG file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def png(file_handle, position, temp_object):
    # print("position in function png:", position)
    temp_object.name = str(position) + ".png"
    temp_object.type = "png"
    temp_object.start = position
    position_png = position
    # look for file end marker
    end_position_png = 0
    # search for end of file
    while position_png < file_size:
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(8))
        if current_bytes == "49454e44ae426082":
            # end of file found
            end_position_png = position_png + 6
            break
        position_png += 1
    temp_object.end = end_position_png
    temp_object.size = temp_object.end - temp_object.start + 1
    # recover file
    recover_file(file_handle, temp_object)
    return 0


# Handles the discovery of an MPG file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def mpg(file_handle, position, temp_object):
    temp_object.name = str(position) + ".mpg"
    temp_object.type = "mpg"
    temp_object.start = position
    position_mpg = position
    end_position_mpg = 0
    # search for end of file
    while position_mpg < file_size - 4:
        file_handle.seek(position_mpg)
        current_bytes = bytes.hex(file_handle.read(4))
        if current_bytes == "000001b9" or current_bytes == "000001b7":
            # end of file found
            end_position_mpg = position_mpg + 3
            break
        position_mpg += 1
    # if end_position_mpg == 0:
    #    end_position_mpg = position_mpg + 7
    temp_object.end = end_position_mpg
    temp_object.size = temp_object.end - temp_object.start + 1
    # recover file
    recover_file(file_handle, temp_object)
    return 0


# Handles the discovery of an PDF file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def pdf(file_handle, position, temp_object):
    # print("position in function png:", position)
    temp_object.name = str(position) + ".pdf"
    temp_object.type = "pdf"
    temp_object.start = position
    position_pdf = position
    # look for file end marker
    end_position_pdf = 0
    current_bytes = ""
    end_position_pdf = 0
    # check for possible different file endings
    while position_pdf < file_size:

        file_handle.seek(position_pdf)
        current_bytes = bytes.hex(file_handle.read(7))
        if current_bytes == "0a2525454f460a" or current_bytes == "0d2525454f460d":
            # possible end of file found
            end_position_pdf = position_pdf + 8

        file_handle.seek(position_pdf)
        current_bytes = bytes.hex(file_handle.read(6))
        if current_bytes == "0a2525454f46":
            # end of file found
            end_position_pdf = position_pdf + 7

        # check for new file type signature
        if end_position_pdf > 0 and current_bytes in specific_signatures:
            break

        file_handle.seek(position_pdf)
        current_bytes = bytes.hex(file_handle.read(9))
        if current_bytes == "0d0a2525454f460d0a":
            # end of file found
            end_position_pdf = position_pdf + 10

        # now scan for start of a new filetype to find the real end of the pdf
        file_handle.seek(position_pdf)
        current_bytes = bytes.hex(file_handle.read(4))
        if end_position_pdf > 0 and current_bytes in specific_signatures:
            break

        # now scan for start of a new filetype to find the real end of the pdf
        file_handle.seek(position_pdf)
        current_bytes = bytes.hex(file_handle.read(8))
        if end_position_pdf > 0 and current_bytes in specific_signatures:
            break

        position_pdf += 1
    temp_object.end = end_position_pdf
    temp_object.size = temp_object.end - temp_object.start + 1
    # recover file
    recover_file(file_handle, temp_object)
    return 0


# Handles the discovery of an GIF file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def gif(file_handle, position, temp_object):
    temp_object.name = str(position) + ".gif"
    temp_object.type = "gif"
    temp_object.start = position
    position_gif = position
    end_position_gif = 0
    current_bytes = ""
    end_position_gif = 0
    # search for end of file
    while position_gif < file_size:
        file_handle.seek(position_gif)
        current_bytes = bytes.hex(file_handle.read(1))

        if current_bytes == "3b":
            # possible end of file found
            end_position_gif = position_gif

        # scan for start of a new filetype to find the real end of the gif
        file_handle.seek(position_gif)
        current_bytes = bytes.hex(file_handle.read(4))
        if end_position_gif > 0 and current_bytes in specific_signatures:
            break

        # scan for start of a new filetype to find the real end of the gif
        file_handle.seek(position_gif)
        current_bytes = bytes.hex(file_handle.read(6))
        if end_position_gif > 0 and current_bytes in specific_signatures:
            break

        # scan for start of a new filetype to find the real end of the gif
        file_handle.seek(position_gif)
        current_bytes = bytes.hex(file_handle.read(8))
        if end_position_gif > 0 and current_bytes in specific_signatures:
            break
        position_gif += 1

    temp_object.end = end_position_gif
    temp_object.size = temp_object.end - temp_object.start + 1
    # recover file
    recover_file(file_handle, temp_object)
    return 0


# Handles the discovery of an BMP file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def bmp(file_handle, position, temp_object):
    file_handle.seek(position + 2)
    temp_object.start = position
    temp_object.size = int.from_bytes(file_handle.read(4), 'little') + 1
    # if bitmap file is too big, do not recover it
    if temp_object.size > 1000000:
        return 1
    # create bmp file object
    temp_object.name = str(temp_object.start) + ".bmp"
    temp_object.end = temp_obj.start + temp_obj.size - 1
    temp_object.type = "bmp"
    # recover file
    recover_file(file_handle, temp_object)
    return 0


# Handles the discovery of an DOCX file in the disk image
## file_handle: The disk image string
## found_temp: Temporary FoundFile object containing pertinent information regarding the file
def docx(file_handle, position, temp_object):
    temp_object.name = str(position) + ".docx"
    temp_object.type = "docx"
    temp_object.start = position
    position_docx = position
    end_position_docx = 0
    # search for end of file
    while position_docx < file_size:
        file_handle.seek(position_docx)
        current_bytes = bytes.hex(file_handle.read(4))
        if current_bytes == "504b0506":
            # end of file found
            end_position_docx = position_docx + 21
            break
        position_docx += 1
    temp_object.end = end_position_docx
    temp_object.size = temp_object.end - temp_object.start + 1
    # recover the file
    recover_file(file_handle, temp_object)
    return 0


# Print the formatted results of the file search
def print_results():
    print("The disk image contains", len(found_files), "files")
    for x in found_files:
        print("Name:", x.name, "\tStart Offset:", hex(x.start), "\tEnd Offset:", hex(x.end), "\nSHA-256:", x.hash)
    return 0


if __name__ == '__main__':

    # get filename for target_file
    filename = sys.argv[-1]
    if filename == sys.argv[0]:
        print("Usage is python3 extract_info.py <filename>")
        exit(0)
    else:
        print("Analyzing file", filename, "for these file signatures:")

    found_files = []  # Array to hold FoundFile objects

    # setup a dictionary for the first byte of the file types searching for. work in string
    first_byte_text = {
        '00': "mpg",
        "25": "pdf",
        "42": "bmp",
        "47": "gif",
        "ff": "jpg",
        "50": "docx",
        "52": "avi",
        "89": "png",
    }

    # setup dictionary for the number of bytes to read based on the first byte
    number_of_bytes = {
        'mpg': 4,
        'pdf': 4,
        'bmp': 2,
        'gif': 4,
        'jpg': 4,
        'docx': 8,
        'avi': 4,
        'png': 8
    }

    # setup dictionary for the signatures and their corresponding file types
    specific_signatures = {
        '000001ba': 'mpg',
        '000001b3': 'mpg',
        '25504446': 'pdf',
        '424d': 'bmp',
        '47494638': 'gif',
        'ffd8ffe0': 'jpg',
        'ffd8ffe1': 'jpg',
        'ffd8ffe2': 'jpg',
        'ffd8ffe3': 'jpg',
        'ffd8ffe4': 'jpg',
        'ffd8ffe5': 'jpg',
        'ffd8ffe6': 'jpg',
        'ffd8ffe7': 'jpg',
        'ffd8ffe8': 'jpg',
        'ffd8ffe9': 'jpg',
        'ffd8ffea': 'jpg',
        'ffd8ffeb': 'jpg',
        'ffd8ffec': 'jpg',
        'ffd8ffed': 'jpg',
        'ffd8ffdb': 'jpg',
        '52494646': 'avi',
        '89504e470d0a1a0a': 'png',
        '504b030414000600': 'docx',
    }

    # detail which files are being searched and with what signatures
    for x in specific_signatures:
        print(specific_signatures[x], "with signature", x)

    # read the analysis file
    try:
        working_file = open(filename, 'rb')
    except IOError:
        print("File not found")
        exit(0)

    position = 0
    file_size = os.path.getsize(filename)

    # iterate through file, find files and save files
    while position < file_size:
        working_file.seek(position)
        current_byte = working_file.read(1)

        # keep user updated with progress
        if position % 10000000 == 0:
            print("Checking file at offset:", position)

        # convert byte to a string
        working_text = bytes.hex(current_byte)

        # if current byte is a potential start to a file signature,
        if working_text in first_byte_text:
            # determine number of bytes to look for
            read_amount = number_of_bytes[first_byte_text[working_text]]
            working_file.seek(position)

            # grab the next read_amount bytes to match against file signatures
            test_signature = bytes.hex(working_file.read(read_amount))

            # now that the correct number of bytes read, try to match against file signatures and handle appropriately
            if test_signature in specific_signatures:
                if specific_signatures[test_signature] == "avi":  ## Explanation for following if statements
                    temp_obj = FoundFile()  # Create new FoundFile object
                    avi(working_file, position, temp_obj)  # Call the necessary function to handle this file type
                    position = temp_obj.end  # Set the position to continue at the end of the found file
                    found_files.append(temp_obj)  # Add the found file to the found_files array
                    working_file.seek(position)  # Set the reader at the end of the file
                if specific_signatures[test_signature] == "jpg":
                    temp_obj = FoundFile()
                    jpg(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "png":
                    temp_obj = FoundFile()
                    png(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "mpg":
                    temp_obj = FoundFile()
                    mpg(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "pdf":
                    temp_obj = FoundFile()
                    pdf(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "gif":
                    temp_obj = FoundFile()
                    gif(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "docx":
                    temp_obj = FoundFile()
                    docx(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "bmp":
                    temp_obj = FoundFile()
                    status = bmp(working_file, position, temp_obj)
                    if status == 0:  # If the bmp file is small enough, it is good to add
                        position = temp_obj.end
                        found_files.append(temp_obj)
                        working_file.seek(position)
        position += 1

    # cleanup by closing the file
    working_file.close()
    print("Printing Results")
    print_results()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/