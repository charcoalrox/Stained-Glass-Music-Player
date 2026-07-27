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
# TODO: PlaylistScrubber deletes descriptions and ruins the playlist titles. Turns em into paths
# TODO: Python can't open certain playlists because it's missing foreign characters. Make sure this is fixed on my computer so I can actually use this software when it's done, please "File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.11_3.11.2544.0_x64__qbz5n2kfra8p0\Lib\encodings\cp1252.py", line 23, in decode
                                                                                                                                                                                            #return codecs.charmap_decode(input,self.errors,decoding_table)[0]"

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


# Display metadata for song and allow user to change any metadata they want to
class playlistEditorWindow(QWidget): 
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setWindowTitle("Edit Playlist Data")

        self.nameTitle = QLabel()
        self.nameTitle.setText("Playlist Name: ")
        self.newName = QLineEdit()
        layout.addWidget(self.nameTitle)
        layout.addWidget(self.newName)

        self.DescTitle = QLabel()
        self.DescTitle.setText("Playlist Description: ")
        self.newDesc = QLineEdit()
        layout.addWidget(self.DescTitle)
        layout.addWidget(self.newDesc)

        self.button = QPushButton("Submit")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.create_playlist)

        self.setLayout(layout)

        self.parent_window = None
        self.selectedPlaylist = None # Song selected when this window is open
        self.playlistToDelete = None

    def create_playlist(self):
        title_text = self.newName.text().strip() # .strip makes sure blank spaces alone don't count as a title
        desc_text = self.newDesc.text().strip().replace("\r", "").replace("\n", "")
        filePath = f"{playlistsPath}//{title_text}.m3u8"
        if self.playlistToDelete is not None: filePath = f"{playlistsPath}//{self.playlistToDelete.text()}"
        file_data = ""

        # create a file if the title is valid
        if title_text:

            # Check if file is real, Copy data if yes
            if os.path.exists(filePath):
                with open(filePath, "r") as f:
                    file_data = f.read()

            if self.playlistToDelete is not None and self.playlistToDelete.text() != f"{title_text}.m3u8" and os.path.exists(f"{playlistsPath}//{self.playlistToDelete.text()}"):
                self.parent_window.delete_playlist(self.playlistToDelete)

            # Write file with provided data from LineEdit elems
            with open(f"{playlistsPath}//{title_text}.m3u8", "w") as f:
                f.write("#EXTM3U\n")
                f.write(f"#{title_text}\n")

                if desc_text:
                    f.write(f"###{desc_text} \n")

                if file_data != "":
                    for line in file_data.splitlines():
                        if not line.startswith('#'):
                            f.write(line + '\n')

            # Automatically close window after editing (if editing existing playlist). Solves issues with path errors after initial edit finishes
            if self.playlistToDelete is not None:
                self.close()

            self.parent_window.display_playlists()

        else: 
            print("ERROR: Need an input title")


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
        
        # Create a new playlist here
        self.button = QPushButton("New Playlist")
        self.button.clicked.connect(lambda: create_new_playlist(self))
        layout.addWidget(self.button)

        # Edit Existing Playlist
        # TODO: This should be a dropdown option
        self.button = QPushButton("Edit Playlist")
        self.button.clicked.connect(lambda: create_new_playlist(self, True, self.playlistList.selectedItems()))
        layout.addWidget(self.button)

        self.button = QPushButton("Delete Playlist")
        self.button.clicked.connect(lambda: self.delete_playlist(self.playlistList.selectedItems()[0]))
        layout.addWidget(self.button)

        # Enable custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda position: show_right_click_menu(self, position)
        ) # Real one will edit playlist names and descriptions

        # Holder vars for child windows of main
        self.fFSongsWindow = None
        self.pCSongsWindow = None
        self.playListEditorWindow = None
        self.selectedPlaylist = None

    # separate window opener funcs

    # display all songs not inside of a playlist
    def window_unused_songs(self, checked):
        self.fFSongsWindow = ForgottenSongsWindow()
        self.fFSongsWindow.show()

    # display all songs inside of playlist
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

    def delete_playlist(self, playlistToDelete):
        targetPath = f"{playlistsPath}//{playlistToDelete.text()}"

        if os.path.exists(targetPath):
            os.remove(targetPath)
            self.display_playlists() # refresh playlists when done
            self.selectionChanged()

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

    if output_playlist is not None: # output_playlist may be "none" if songs are just being deleted from current playlist instead of moved
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
        fileName = (playlistsPath + "//" + input_playlist)

        with open (fileName, "r+") as f: # this probably won't cut it. I'm going to read this file and then overwrite it with lines missing
            print("Stuff here later")
            # Read over everything
            # skip lines containing a song from the selected songs array
            # overwrite playlist with new output no longer containing selected songs




        # I guess we iterate over each playlist element and check if they're the current song? I assume we'll have less songs than playlist items selected in most cases so this is bad but shorter

# def copy_to_playlist(self, selected_items):
#     print("Songs are to be copied to playlist")
#     if selected_items is not None:
#         for i in selected_items:
#             print(i.text())
#     else: 
#         print("ERROR: No items selected or something has gone wrong (line 313)")

#generate a new playlist with it's own description
# Global so that I can make this a dropdown menu option that also exists on basically every window
def create_new_playlist(self, overwrite = False, selectedPlaylist = None):

    self.playListEditorWindow = playlistEditorWindow()
    self.playListEditorWindow.selectedPlaylist = self.selectedPlaylist
    if overwrite: self.playListEditorWindow.playlistToDelete = self.selectedPlaylist
    self.playListEditorWindow.parent_window = self
    self.playListEditorWindow.show()

    if self.selectedPlaylist is not None and overwrite == True:
        self.playListEditorWindow.newName.setText(self.selectedPlaylist.text()[:-5])
        with open(f"{playlistsPath}//{self.selectedPlaylist.text()}", "r") as f:
            for line in f:
                if line.startswith("###"):
                    self.playListEditorWindow.newDesc.setText(line[3:])

if __name__ == "__main__":
    ScanFilePaths()

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()