#!/usr/bin/python3
### scan all m3u and m3u8 files in a directory. Clean contents, remove duplicates, reformat all files to type .m3u8 (better compatibility)
### Makes playlists run on my computer and my phone more easily

import os

# Clean file contents and add them to an array for further modification
def initializeFileAsArray(fileName, fileContentsArray):

    # Create metadata at top of m3u8 file
    fileContentsArray.append("#EXTM3U\n")

    titleFormatter = fileName.split('.')
    playListTitle = "#{0}\n".format(titleFormatter[0])
    fileContentsArray.append(playListTitle)

    # Read contents by line
    with open(fileName, "r", encoding='utf-8', errors='ignore') as f:
        for x in f: 
            if x[0] == '#' or x[0] == '\n': # ignore blank lines and comments
                pass
            elif x[0] != '.' and x[1] != '.': # Check if a line contains a non-local filepath
                splitStringArray = x.split('\\') # Convert file path to local
                if len(splitStringArray) > 1:
                    newPath = "..\\{0}".format(splitStringArray[len(splitStringArray) - 1]) 
                    fileContentsArray.append(newPath)
                else:
                    pass
            else: # add valid filepaths to array
                fileContentsArray.append(x)

    return fileContentsArray


# blatantly stolen from: https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
def RemoveDuplicates(fileContentsArray):
    seen = set()
    uniq = []
    for x in fileContentsArray:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return uniq


def cleanFiles(filepath):
    fileNames = [] # all playlists in current directory
    currentFileContents = [] # contents of currently loaded file

    for file in os.listdir(filepath):
        if file.endswith(".m3u") or file.endswith(".m3u8"):
            fileNames.append(os.path.join(filepath, file))

    for currentFile in fileNames:

        currentFileContents = [] # reset file contents on each run

        currentFileContents = initializeFileAsArray(currentFile, currentFileContents) #First pass: Open file, add valid inputs to an array
        currentFileContents = RemoveDuplicates(currentFileContents) # Second Pass: remove duplicate songs

        # Write modified contents of playlist to disk
        os.remove(currentFile) # Remove original file so I can modify it's type (Dangerous. Maybe even cool?)

        titleSplit = currentFile.split(".")
        newFileName = "{0}.m3u8".format(titleSplit[0]) # ensure the file extension is correct

        with open(newFileName, "w", encoding='utf-8', errors='ignore') as f:
            for contents in currentFileContents:
                f.write(contents)

    # print("Files have been processed")

# if __name__ == "__main__":
#     cleanFiles("C:\\Users\\payto\\OneDrive\\Desktop\\Music Project\\Playlists")
