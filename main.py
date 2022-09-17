import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog
from typing import List, Tuple

from playsound import playsound

import diarization


class MainWindow(tk.Frame):
    master: tk.Tk

    def __init__(self, master: tk.Tk = None):
        super().__init__(master)

        column_names = {
            'file_name': 'File Name',
            'german': 'German',
            'join': 'Join',
            'out_name': 'Out Name'
        }

        self.treeview = ttk.Treeview(self.master, columns=tuple(column_names.keys()), show='headings')

        for column, header in column_names.items():
            self.treeview.heading(column, text=header)

        self.treeview.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self._configure_menubar()
        self._configure_key_bindings()

        self.available_mp3s: List[Tuple[str, str, str, str]] = []
        self.selected_folder = Path('.').absolute()

    def _configure_key_bindings(self):
        self.treeview.bind('<space>', self.play_audio)

    def _configure_menubar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Open Folder', command=self.open_folder)

        menubar.add_cascade(label='File', menu=file_menu)

    def open_folder(self):
        self.selected_folder = filedialog.askdirectory()
        self.available_mp3s = []
        
        diarized = diarization.diarize_files(list(Path(self.selected_folder).glob('*.mp3')),
                                             {"Deutsch": Path("all_deu.mp3"), "Englisch": Path("all_eng.mp3")},
                                             True, True)

        for file, similarity in diarized.items():
            self.available_mp3s.append((file.name, str(similarity['Deutsch'] > similarity['Englisch']), '', ''))

        self.redraw()

    def redraw(self):
        self.treeview.delete(*self.treeview.get_children())
        for mp3 in self.available_mp3s:
            self.treeview.insert('', tk.END, values=mp3)

    def play_audio(self, event: tk.Event):
        for selection in self.treeview.selection():
            cols = self.treeview.item(selection)['values']
            playsound(Path(cols[0]).absolute())  # TODO


def main():
    root = tk.Tk()
    root.title('Audio Splitter Editor')
    window = MainWindow(root)

    root.mainloop()


if __name__ == '__main__':
    main()
