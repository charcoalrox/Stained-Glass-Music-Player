#!/usr/bin/env python3
### m3u playlist editor that prepares files for transfer to my phone and allows bulk file movement
import sys
import os
import re

import findForgottenSongs
import m3uCleaner

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QListWidget

# TODO: Import these from paths.json instead of hardcoding them here
# TMP: filepaths here for ease of use. Eventually these will be imported from paths.json on starup
pathListPath = "C:\\Users\\payto\\OneDrive\\Desktop\\Music Project\\Stained-Glass-Music-Player\\paths.json" # One hard-coded path to avoid many more hard-coded paths
songspath = ""
playlistsPath = ""

# Lists songs not yet put into a playlist. Popup Window (disabled by default)
class ForgottenSongsWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Songs not in playlists")

        # Define list of songs not currently in a playlist
        self.songsListWidget = QListWidget()
        layout.addWidget(self.songsListWidget)

        self.button = QPushButton("Refresh")
        self.button.clicked.connect(self.refresh_list)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.refresh_list()

    # Scan through all playlists/songs. Find songs not currently available
    def refresh_list(self):
        self.songsListWidget.clear()
        self.songsListWidget.addItems(findForgottenSongs.songSearch(playlistsPath, songspath))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Playlist Editor")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Display all playlists in list
        self.playlistList = QListWidget()
        self.display_playlists()
        layout.addWidget(self.playlistList)

        # Access unsued songs window
        self.button = QPushButton("Find Forgotten Songs")
        self.button.clicked.connect(self.show_new_window)
        layout.addWidget(self.button)

        self.button = QPushButton("Playlist Scrubber")
        self.button.clicked.connect(self.m3u_repair)
        layout.addWidget(self.button)

        self.fFSongsWindow = None

    def show_new_window(self, checked):
        self.fFSongsWindow = ForgottenSongsWindow()
        self.fFSongsWindow.show()

    def m3u_repair(self):
        m3uCleaner.cleanFiles(playlistsPath)
        self.display_playlists()

    def display_playlists(self):
        self.playlistList.clear()

        for file in os.listdir(playlistsPath):
            if file.endswith(".m3u8") or file.endswith(".m3u"):
                self.playlistList.addItem(file)


#TODO: I can set all of these variables inside of a data structure and iterate over the names in a single loop. Way faster
# Initialize file paths before running software
def ScanFilePaths():
    with open(pathListPath, "r") as f:
        global songspath
        global playlistsPath

        for lines in f:
            if lines.startswith("songs"):
                matches = re.findall(r'"([^"]*)"', lines)
                songspath = matches[0]
            if lines.startswith("playlists"):
                matches = re.findall(r'"([^"]*)"', lines)
                playlistsPath = matches[0]
    f.close()


ScanFilePaths()

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()