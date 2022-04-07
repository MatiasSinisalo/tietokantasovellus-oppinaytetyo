from werkzeug.utils import secure_filename
import os

#This function creates a temporary file, gets its content and removes the file
def ReturnUploadedFileContents(content, ALLOWED_EXTENSIONS, UPLOAD_FOLDER):
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

        #Remove the file as it is no longer needed
        removeFile(pathToFile)
        return bookString
    else:
        return False

def removeFile(FilePathToRemove):
    if FilePathToRemove:
        if os.path.exists(FilePathToRemove):
            os.remove(FilePathToRemove)
            return True
    return False