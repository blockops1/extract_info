import binascii
import hashlib
import os
import sys
import time


class IterRegistry(type):
    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("__"):
                yield attr


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


def recover_file(file_handle, found_temp):
    path = "files"
    if not os.path.exists(path):
        os.makedirs(path)
    file_handle.seek(found_temp.start)
    output_file = open(os.path.join(path, found_temp.name), 'wb')
    output_file.write(file_handle.read(found_temp.size))
    output_file.close()
    hash_file = open(os.path.join(path, found_temp.name), 'rb')
    hash_file_full = hash_file.read()
    hash_file.close()
    hash_sha256 = hashlib.sha256(hash_file_full).hexdigest()
    found_temp.hash = hash_sha256
    x = found_temp
    print("found a file - name:", x.name, "type:", x.type, "start:", x.start, "end:", x.end, "size:", x.size)
    return 0


def avi(file_handle, position, temp_object):
    # print("position in function avi:", position)
    file_handle.seek(position + 4)
    temp_object.start = position
    temp_object.size = int.from_bytes(file_handle.read(4), 'little') + 8
    # create avi file object, recover file, and computes sha256
    temp_object.name = str(temp_object.start) + ".avi"
    temp_object.end = temp_obj.start + temp_obj.size
    temp_object.type = "avi"
    # print("calling recover file for avi")
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    recover_file(file_handle, temp_object)
    file_handle.seek(position)
    return 0


def jpg(file_handle, position, temp_object):
    # print("position in function jpg:", position)
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
    temp_object.size = temp_object.end - temp_object.start
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    # print("calling recover file for jpg")
    recover_file(file_handle, temp_object)
    return 0


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
            end_position_png = position_png + 7
            break
        position_png += 1
    temp_object.end = end_position_png
    temp_object.size = temp_object.end - temp_object.start
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    # print("calling recover file for jpg")
    recover_file(file_handle, temp_object)
    return 0


def mpg(file_handle, position, temp_object):
    # print("position in function png:", position)
    temp_object.name = str(position) + ".mpg"
    temp_object.type = "mpg"
    temp_object.start = position
    position_png = position
    # look for file end marker
    end_position_png = 0
    # search for end of file
    while position_png < file_size - 4:
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(4))
        if current_bytes == "000001b9" or current_bytes == "000001b7":
            # end of file found
            end_position_png = position_png
            break
        position_png += 1
    if end_position_png == 0:
        end_position_png = position_png + 7
    temp_object.end = end_position_png
    temp_object.size = temp_object.end - temp_object.start
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    # print("calling recover file for mpg")
    time.sleep(5)
    recover_file(file_handle, temp_object)
    return 0


def pdf(file_handle, position, temp_object):
    # print("position in function png:", position)
    temp_object.name = str(position) + ".pdf"
    temp_object.type = "pdf"
    temp_object.start = position
    position_png = position
    # look for file end marker
    end_position_png = 0
    # search for end of file
    current_bytes = ""
    end_position_png = 0
    while position_png < file_size:
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(7))
        if current_bytes == "0a2525454f460a" or current_bytes == "0d2525454f460d":
            # possible end of file found
            end_position_png = position_png + 7
            # print("possible pdf ending string:", end_position_png)
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(6))
        if current_bytes == "0a2525454f46":
            # end of file found
            end_position_png = position_png + 6
            # print("possible pdf ending string:", end_position_png)
        # check for new file type signature
        if end_position_png > 0 and current_bytes in specific_signatures:
            # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
            break
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(9))
        if current_bytes == "0d0a2525454f460d0a":
            # end of file found
            end_position_png = position_png + 9
            # print("possible pdf ending string:", end_position_png)
        # now scan for start of a new filetype to find the real end of the pdf
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(4))
        if end_position_png > 0 and current_bytes in specific_signatures:
            # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
            break
        # now scan for start of a new filetype to find the real end of the pdf
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(8))
        if end_position_png > 0 and current_bytes in specific_signatures:
            # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
            break
        position_png += 1
    # print("pdf ending string position:", end_position_png)
    # time.sleep(5)
    temp_object.end = end_position_png
    temp_object.size = temp_object.end - temp_object.start
    x = temp_object
    recover_file(file_handle, temp_object)
    return 0


def gif2(file_handle, position, temp_object):
    # print("position in function png:", position)
    temp_object.name = str(position) + ".gif"
    temp_object.type = "gif"
    temp_object.start = position
    position_png = position
    # look for file end marker
    end_position_png = 0
    # search for end of file
    current_bytes = ""
    end_position_png = 0
    while position_png < file_size:
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(1))
        if current_bytes == "3b":
            # possible end of file found
            end_position_png = position_png
            # print("possible pdf ending string:", end_position_png)
        # check for new file type signature
        # if end_position_png > 0 and current_bytes in specific_signatures:
        # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
        # break
        # now scan for start of a new filetype to find the real end of the gif
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(4))
        if end_position_png > 0 and current_bytes in specific_signatures:
            # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
            break
        # now scan for start of a new filetype to find the real end of the gif
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(6))
        if end_position_png > 0 and current_bytes in specific_signatures:
            # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
            break
        # now scan for start of a new filetype to find the real end of the gif
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(8))
        if end_position_png > 0 and current_bytes in specific_signatures:
            # print("matched signature:", current_bytes, " for:", specific_signatures[current_bytes])
            break
        position_png += 1
    # print("pdf ending string position:", end_position_png)
    # time.sleep(5)
    temp_object.end = end_position_png
    temp_object.size = temp_object.end - temp_object.start
    x = temp_object
    recover_file(file_handle, temp_object)
    return 0


def gif(file_handle, position, temp_object):
    # print("position in function png:", position)
    temp_object.name = str(position) + ".gif"
    temp_object.type = "gif"
    temp_object.start = position
    position_png = position
    # look for file end marker
    end_position_png = 0
    # search for end of file
    while position_png < file_size:
        file_handle.seek(position_png)
        current_bytes = bytes.hex(file_handle.read(2))
        if current_bytes == "003b":
            # possible end of file found
            end_position_png = position_png
            break
        position_png += 1
    temp_object.end = end_position_png
    temp_object.size = temp_object.end - temp_object.start
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    # print("calling recover file for jpg")
    recover_file(file_handle, temp_object)
    return 0


def bmp(file_handle, position, temp_object):
    # print("position in function avi:", position)
    file_handle.seek(position + 2)
    temp_object.start = position
    temp_object.size = int.from_bytes(file_handle.read(4), 'little') + 1
    # print("bmp size:", temp_object.size)
    if temp_object.size > 1000000:
        return 1
    # create avi file object, recover file, and computes sha256
    temp_object.name = str(temp_object.start) + ".bmp"
    temp_object.end = temp_obj.start + temp_obj.size
    temp_object.type = "bmp"
    # print("calling recover file for avi")
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    recover_file(file_handle, temp_object)
    file_handle.seek(position)
    return 0


def docx(file_handle, position, temp_object):
    # print("position in function jpg:", position)
    temp_object.name = str(position) + ".docx"
    temp_object.type = "docx"
    temp_object.start = position
    position_jpg = position
    # look for file end marker
    end_position_jpg = 0
    # search for end of file
    while position_jpg < file_size:
        file_handle.seek(position_jpg)
        current_bytes = bytes.hex(file_handle.read(4))
        if current_bytes == "504b0506":
            # end of file found
            end_position_jpg = position_jpg + 22
            break
        position_jpg += 1
    temp_object.end = end_position_jpg
    temp_object.size = temp_object.end - temp_object.start
    # x = temp_object
    # print("name: ", x.name, " type:", x.type, " start:", x.start, " end:", x.end, " size:", x.size, " hash:", x.hash)
    # print("calling recover file for jpg")
    recover_file(file_handle, temp_object)
    return 0


def print_results():
    for x in found_files:
        print("name:", x.name, "start:", hex(x.start), "end:", hex(x.end), "hash:",
              x.hash)
        # print("size:", x.size, "difference:", x.end - x.start - x.size)
    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # get filename for target_file
    filename = sys.argv[-1]
    if filename == sys.argv[0]:
        print("usage is python3 extract_info.py <filename>")
        exit(0)
    else:
        print("analyzing file", filename, "for these file signatures:")
    found_files = []
    object_counter = 0
    # setup signature hash table
    # setup a key/value dictionary for the first byte of the file types searching for. work in string
    first_byte_text = {'00': "mpg", "25": "pdf", "42": "bmp", "47": "gif", "ff": "jpg", "50": "docx",
                       "52": "avi", "89": "png"}
    # setup key/value number of bytes to read based on the first byte
    number_of_bytes = {'mpg': 4, 'pdf': 4, 'bmp': 2, 'gif': 4, 'jpg': 4, 'docx': 8, 'avi': 4, 'png': 8}
    specific_signatures = {}
    # read signatures from file signature.txt
    try:
        signature_file = open("signatures.txt")
    except IOError:
        print("Signature file not found")
        exit(0)
    while True:
        sig = signature_file.readline()
        if len(sig) == 0:
            break
        name = signature_file.readline()
        if len(name) == 0:
            break
        specific_signatures[sig.rstrip()] = name.rstrip()
    for x in specific_signatures:
        print(specific_signatures[x], "with signature", x)
    # read the analysis file
    try:
        working_file = open(filename, 'rb')
    except IOError:
        print("File not found")
        exit(0)
    # print("first byte text", first_byte_text)
    # print("number of bytes", number_of_bytes)
    # for x in first_byte_text:
    #    print(x, first_byte_text[x], number_of_bytes[first_byte_text[x]])
    position = 0
    file_size = os.path.getsize(filename)
    file_size = 60000000
    while position < file_size:
        working_file.seek(position)
        current_byte = working_file.read(1)
        # convert to integer
        # working_number = int.from_bytes(current_byte, 'big')
        if position % 10000000 == 0:
            print("checking file at offset:", position)
        # convert byte to a string
        working_text = bytes.hex(current_byte)
        if working_text in first_byte_text:
            # get number of bytes to read
            # if working_text == "ff":
            #  print("at position", position, "byte is", working_text)
            read_amount = number_of_bytes[first_byte_text[working_text]]
            # if position == 229376:
            #    print("at position 229376, byte is", working_text, "read amount is", read_amount)
            working_file.seek(position)
            test_signature = bytes.hex(working_file.read(read_amount))
            # if working_text == "ff":
            #    print("at position", position, "working text", working_text, first_byte_text[working_text],
            #          number_of_bytes[first_byte_text[working_text]], read_amount, "test signature", test_signature)
            # now that the correct number of bytes read, try to match against file signatures
            if test_signature in specific_signatures:
                # print("offset:", position, " signature:", test_signature, " file type:", specific_signatures[test_signature])
                if specific_signatures[test_signature] == "avi":
                    # print("matched signature:", test_signature, " for:", specific_signatures[test_signature])
                    temp_obj = FoundFile()
                    avi(working_file, position, temp_obj)
                    position = temp_obj.end
                    found_files.append(temp_obj)
                    working_file.seek(position)
                if specific_signatures[test_signature] == "jpg":
                    # print("matched signature:", test_signature, " for:", specific_signatures[test_signature])
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
                    gif2(working_file, position, temp_obj)
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
                    if status == 0:
                        position = temp_obj.end
                        found_files.append(temp_obj)
                        working_file.seek(position)
        position += 1
    # cleanup by closing the file
    working_file.close()
    print("printing results")
    # print(found_files)
    print_results()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
