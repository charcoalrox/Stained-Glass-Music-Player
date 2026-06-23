#!/usr/bin/python3
### List any songs that aren't present in any playlists
### !!!Formatting assumes you've run m3u cleaner first or it won't work right!!!
    ### playlists must use a local file path. Too many edge cases for this to be more modular than it is

import os


# Wikipedia says this is every audio file format ever. Please no one make more (https://en.wikipedia.org/wiki/Audio_file_format)
FILE_EXTENSIONS = [
    ".mp3",
    ".wav",
    ".flac",
    ".m4a",
    ".ogg", # The ones I've actually seen used at the top (for speed)
    ".3gp",
    ".aa",
    ".aac",
    ".aax",
    ".act",
    ".aiff",
    ".alac",
    ".amr",
    ".ape",
    ".au",
    ".awb",
    ".dss",
    ".dvf",
    ".gsm",
    ".iklax",
    ".ivs",
    ".m4b",
    ".m4p",
    ".mmf",
    ".movpkg",
    ".mp1",
    ".mp2",
    ".mpc",
    ".msv",
    ".nmf",
    ".oga",
    ".mogg",
    ".opus",
    ".ra",
    ".rm",
    ".raw",
    ".rf64",
    ".sln",
    ".tta",
    ".voc",
    ".vox",
    ".wma",
    ".wv",
    ".webm",
    ".8svx",
    ".cda",
]

# In case there are playlists I don't want to check for songs (like if I have a favorites playlist)
Exclusions = [
    "Cream of the Crop!.m3u8"
]


def songSearch(playlistspath, songspath):
    playlistNames = [] # all playlists in current directory
    missedFilesCount = 0

    # Scan all playlists
    for file in os.listdir(playlistspath):
        if (file.endswith(".m3u") or file.endswith(".m3u8")) and file not in Exclusions:
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
            for fe in FILE_EXTENSIONS: # only valid audio files not in a playlist will display here
                if file.endswith(fe):
                    stragglerFiles.append(file)
                    # print(file)
                    missedFilesCount += 1
                    break

    return stragglerFiles

# if __name__ == "__main__": # This is here in case I have a change of heart but I don't think this is going to be runnable via command line
#     songSearch()