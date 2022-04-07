from werkzeug.utils import secure_filename
import os

def addAndReturnUploadedFile(content, ALLOWED_EXTENSIONS, UPLOAD_FOLDER):
    filename = content.filename
    pathToFile = ''
    if filename.split(".", 1)[1] in ALLOWED_EXTENSIONS:
        filenameToWrite = secure_filename(filename)
        pathToFile = os.path.join(UPLOAD_FOLDER, filenameToWrite)
        #save the uploaded file to server disk
        content.save(pathToFile)
        content.close()
        
        #Read the file from server disk
        file = open(pathToFile, "r")
        bookString = "".join(file.readlines())
        file.close()
        return bookString
    else:
        return False

