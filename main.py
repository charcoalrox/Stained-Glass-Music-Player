#!/usr/bin/env python3
### m3u playlist editor that prepares files for transfer to my phone and allows bulk file movement
import sys
import os
import re

import find_forgotten_songs
import m3u_cleaner

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QListWidget, QApplication, QAbstractItemView


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
        self.songsListWidget.addItems(find_forgotten_songs.songSearch(playlistsPath, songspath))


class PlaylistViewerWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Playlist view") # TODO: Set this to the playlist name

        self.playlistDescription = QLabel()
        self.playlistDescription.setText(" ")
        layout.addWidget(self.playlistDescription)

        self.songsListWidget = QListWidget()
        layout.addWidget(self.songsListWidget)

        self.button = QPushButton("Play")
        self.button.clicked.connect(self.play_song)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.selectedPlaylist = None

    def prep_Window(self):
        self.setWindowTitle(self.selectedPlaylist.text()[:-5])  #TODO: Scrape off file extension

        fileName = (playlistsPath + "//" + self.selectedPlaylist.text())
        with open(fileName, "r", encoding='utf-8', errors='ignore') as f:
            for x in f: 
                if x[0] == '#' and x[1] == '#' and x[2] == '#': # Set playlist description if present
                    self.playlistDescription.setText(x[3:])
                elif x[0] == '#' or x[0] == '\n': # ignore blank lines and comments
                    pass
                else: # Display remaining files that contain a file extension
                    self.songsListWidget.addItem(x[3:].strip())
        f.close()

    def play_song(self):
        print("This will do something eventually")
        print(self.selectedPlaylist.text())


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
        self.playlistList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.playlistList.itemSelectionChanged.connect(self.selectionChanged)
        self.display_playlists()
        layout.addWidget(self.playlistList)

        # Access unsued songs window
        self.button = QPushButton("Find Forgotten Songs")
        self.button.clicked.connect(self.window_unused_songs)
        layout.addWidget(self.button)

        # Display contents of selected playlist
        self.button = QPushButton("Open Playlist")
        self.button.clicked.connect(self.window_playlist_contents)
        layout.addWidget(self.button)

        # Modify playlists into a generalized .m3u8 format
        self.button = QPushButton("Playlist Scrubber")
        self.button.clicked.connect(self.m3u_repair)
        layout.addWidget(self.button)

        self.fFSongsWindow = None
        self.pCSongsWindow = None
        self.selectedPlaylist = None

    # separate window opener funcs
    def window_unused_songs(self, checked):
        self.fFSongsWindow = ForgottenSongsWindow()
        self.fFSongsWindow.show()

    def window_playlist_contents(self):
        print("Selected items: ", self.playlistList.selectedItems())

        if self.selectedPlaylist is not None:
            self.pCSongsWindow = PlaylistViewerWindow()
            self.pCSongsWindow.selectedPlaylist = self.selectedPlaylist
            self.pCSongsWindow.prep_Window()
            self.pCSongsWindow.show()
        else: # TODO: We should have an invisible label for error messages like this
            print("ERROR: Please select a playlist to proceed")

    # Store current playlistList selection into a variable for later use
    def selectionChanged(self):
        self.selectedPlaylist = self.playlistList.currentItem()

    # m3u repair script
    def m3u_repair(self):
        m3u_cleaner.cleanFiles(playlistsPath)
        self.display_playlists()

    # Refresh central playlist list
    def display_playlists(self):
        self.playlistList.clear()

        for file in os.listdir(playlistsPath):
            if file.endswith(".m3u8") or file.endswith(".m3u"):
                self.playlistList.addItem(file)


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