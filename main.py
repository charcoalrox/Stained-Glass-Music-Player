#!/usr/bin/env python3
### m3u playlist editor that prepares files for transfer to my phone and allows bulk file movement
import sys
import os
import re
from tinytag import TinyTag # Displays and edits song metadata

import find_forgotten_songs
import m3u_cleaner

# TODO: combine like includes
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QListWidget, QApplication, QAbstractItemView, QLineEdit, QAbstractItemView
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
from PyQt5.QtCore import Qt

# TODO: printing songs in a list is a global function usable by all classes
# TODO: Music is played on main window. If you play music from any other function is merely passes to the main window which can kill other songs
# TODO: Refresh open playlist whenever a song is added to a playlist from any window. This is my biggest gripe with WMP if we don't fix it then what was the point?
# TODO: Relative paths mean I need a constant CWD. Either make paths global or find a way to ensure the cwd is always the dir containing main when this program is run or it will fail
# TODO: Flag relevant lists as either select one or select all and change how I access their contents

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
        self.songsListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection) # Enables multi-item list selections

        self.button = QPushButton("Refresh")
        self.button.clicked.connect(self.refresh_list)
        layout.addWidget(self.button)

        # Enable custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda position: edit_songs_menu(self, position, self.songsListWidget.selectedItems())
        ) # Real one will edit playlist names and descriptions

        # Run these functions once automatically while setting up with window
        self.setLayout(layout)
        self.refresh_list()

    # Scan through all playlists/songs. Find songs not currently available
    def refresh_list(self):
        self.songsListWidget.clear()
        self.songsListWidget.addItems(find_forgotten_songs.songSearch(playlistsPath, songspath))


# Lists contents of a single playlist in own window
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

        self.button = QPushButton("Edit Song")
        self.button.clicked.connect(self.open_metadata_editor)
        layout.addWidget(self.button)

        self.player = QMediaPlayer()

        self.setLayout(layout)

        self.selectedPlaylist = None # Playlist passed from main window when this is opened
        self.mDSongsWindow = None # Holder variable for the Meta Data Song editor window

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
        url = QUrl.fromLocalFile(str("../" + self.songsListWidget.selectedItems()[0].text()))
        self.player.setMedia(QMediaContent(url))
        self.player.play()
        
    def open_metadata_editor(self):
        print("Selected item: ", self.songsListWidget.selectedItems())
        self.mDSongsWindow = metadata_window()
        self.mDSongsWindow.selectedSong = TinyTag.get("../" + self.songsListWidget.selectedItems()[0].text())
        self.mDSongsWindow.show()


# Display metadata for song and allow user to change any metadata they want to
class metadata_window(QWidget): 
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Edit Song Metadata") # TODO: Set this to the Song name

        self.playlistDescription = QLabel()
        self.playlistDescription.setText(" ")
        layout.addWidget(self.playlistDescription)

        self.newName = QLineEdit()
        layout.addWidget(self.newName)

        self.button = QPushButton("Submit")
        layout.addWidget(self.button)
        # TODO: HOok this up to a function that updates metadata with everything inside of the lineedit widget

        self.setLayout(layout)

        self.selectedSong = None # Song selected when this window is open


# Default window. Displays all playlists and allows opening of other windows
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

        # Enable custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda position: show_right_click_menu(self, position)
        ) # Real one will edit playlist names and descriptions

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
        else:
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

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()


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


# Example code for a menu. Not real, ignore
def show_right_click_menu(self, position):
    # 3. Create the QMenu container
    context_menu = QMenu(self)

    # 4. Define individual menu options
    action_one = QAction("Option One", self)
    action_two = QAction("Option Two", self)
    action_exit = QAction("Exit Application", self)

    # 5. Attach functional triggers to each action
    action_one.triggered.connect(lambda: print("Option One clicked!"))
    action_two.triggered.connect(lambda: print("Option Two clicked!"))
    action_exit.triggered.connect(self.close)

    # 6. Load actions into the context menu
    context_menu.addAction(action_one)
    context_menu.addAction(action_two)
    context_menu.addSeparator()  # Adds a physical visual line divider
    context_menu.addAction(action_exit)

    context_menu.addSeparator()

    # 4. Create the nested dropdown menu (Submenu)
    dropdown_menu = QMenu("Settings Dropdown", self)

    # 5. Add options inside the dropdown menu
    option1 = QAction("Enable Dark Mode", self)
    option1.triggered.connect(lambda: print("Dark Mode Toggled"))
    dropdown_menu.addAction(option1)

    option2 = QAction("Reset to Default", self)
    option2.triggered.connect(lambda: print("Settings Reset"))
    dropdown_menu.addAction(option2)

    # 6. Attach the dropdown menu to the main context menu
    context_menu.addMenu(dropdown_menu)

    # 7. Render menu directly at the cursor's absolute screen coordinates
    global_position = self.mapToGlobal(position)
    context_menu.exec_(global_position)


# context menu for right clicking on songs
def edit_songs_menu(self, position, selected_items):
    context_menu = QMenu(self)

    # Dropdown with all playlists added to it
    action_one = QMenu("Copy song(s) to new playlist")
    for file in os.listdir(playlistsPath):
        if file.endswith(".m3u8") or file.endswith(".m3u"):
            action = action_one.addAction(file)

            # Connect the action to a function
            action.triggered.connect(
                lambda checked=False, playlist=file:
                    copy_songs_to_playlist(self, playlist, selected_items)
            )

    # This can be done by passing in a playlist name when calling this menu and then having an alternate, grayed out button when it's none (or just no button?)
    # I'm thinking nothing
    action_two = QAction("Move song(s) to new playlist") # grayed out in find forgotten songs, obviously
    # action_three = QAction("Edit song data") # Modify song name and metadata. Requires refreshing all menus and checking every playlist to make sure song is updated correctly. Might be stupid and expensive

    # action_one.triggered.connect(lambda: copy_to_playlist(self, selected_items))
    action_two.triggered.connect(lambda: print("This will eventually make a dropdown such that ALL selected songs will be m"))

    action_three = QAction("Remove Song(s) from Playlist") # TODO: I can use the existing function, plug "none" into the output func, and keep the input playlist for the input func to make this one work
    action_three.triggered.connect(lambda: print("This is going to delete selected songs from current playlist without moving them somewhere new"))

    # context_menu.addAction(action_one)
    context_menu.addMenu(action_one)
    context_menu.addAction(action_two)

    global_position = self.mapToGlobal(position)
    context_menu.exec_(global_position)


# copies all songs to a new playlist. Optionally deletes them from current playlist
def copy_songs_to_playlist(self, output_playlist, songs, input_playlist = None):
    fileName = (playlistsPath + "//" + output_playlist)

    with open(fileName, "rb+") as f:
        # Go to the end of the file
        f.seek(0, os.SEEK_END)
        pos = f.tell()

        # step backwards over windows newline char returns
        while pos > 0:
            pos -= 1
            f.seek(pos)

            c = f.read(1)
            if c not in (b"\r", b"\n"):
                break
        f.truncate(pos + 1)

        # Make sure we're at the EOF and add all selected songs
        f.seek(0, os.SEEK_END)

        for song in songs:
            f.write(f"\n..\\{song.text()}".encode("utf-8"))

        f.write(b"\n")
    
    # Optoinally, remove selected songs from the currently opened playlist
    if input_playlist is not None:
        print("This shouldn't be possible yet, what?")
        # I guess we iterate over each playlist element and check if they're the current song? I assume we'll have less songs than playlist items selected in most cases so this is bad but shorter

# def copy_to_playlist(self, selected_items):
#     print("Songs are to be copied to playlist")
#     if selected_items is not None:
#         for i in selected_items:
#             print(i.text())
#     else: 
#         print("ERROR: No items selected or something has gone wrong (line 313)")


if __name__ == "__main__":
    ScanFilePaths()

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()