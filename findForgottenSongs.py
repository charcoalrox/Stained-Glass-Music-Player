#!/usr/bin/python3
### List any songs that aren't present in any playlists
### !!!Formatting assumes you've run m3u cleaner first or it won't work right!!!

# TODO: Rename to fit irl Python naming scheme, 
# TODO: exclude favorites playlist, 
# TODO: take an external filepath as input to func so that I can decide where the playlists and songs are located globally
# TODO: Perhaps some regex or something so that only music files display here

import os

def songSearch(playlistspath, songspath):
    playlistNames = [] # all playlists in current directory
    missedFilesCount = 0

    # Scan all playlists
    for file in os.listdir(playlistspath):
        if file.endswith(".m3u") or file.endswith(".m3u8"):
            playlistNames.append(os.path.join(playlistspath, file))

    # make a list of all unique songs in playlist
    seen = set()
    uniq = []
    for currentFile in playlistNames:
        with open(currentFile, "r", encoding='utf-8', errors='ignore') as f:
            for i in f:
                if i[0] != '#': # ignore comments and metadata in file
                    iTitle = i[3:].strip() # Remove file path chars and converts string to proper song title
                    if iTitle not in seen:
                        uniq.append(iTitle)
                        seen.add(iTitle)

    # iterate over music files and compare to playlist files
    stragglerFiles = []
    for file in os.listdir(songspath):
        if file not in seen:
            stragglerFiles.append(file)
            print(file)
            missedFilesCount += 1

    print(missedFilesCount)
    print("Files have been processed")
    return stragglerFiles

# if __name__ == "__main__":
#     songSearch()