import json
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List

from playsound import playsound

import diarization


class MainWindow(tk.Frame):
    master: tk.Tk

    def __init__(self, master: tk.Tk = None):
        super().__init__(master)

        column_names = {
            'file_name': 'File Name',
            'german': 'German',
        }

        self.treeview = ttk.Treeview(self.master, columns=tuple(column_names.keys()), show='headings')

        for column, header in column_names.items():
            self.treeview.heading(column, text=header)

        self.treeview.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        self.treeview.tag_configure('german', background='grey')
        self.treeview.tag_configure('englisch', background='orange')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.german_count_lbl = tk.Label(self.master, text='German Count: ')
        self.german_count_lbl.grid(row=1, column=0, columnspan=1, sticky='ew')

        self._configure_menubar()
        self._configure_key_bindings()

        self.available_mp3s: List[List] = []
        self.selected_folder = Path('.').absolute()

    def _configure_key_bindings(self):
        self.treeview.bind('<space>', self.play_audio)
        self.treeview.bind('d', self.mark_german)

    def _configure_menubar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Open Folder', command=self.open_folder)
        file_menu.add_command(label='Export JSON', command=self.export_json)

        menubar.add_cascade(label='File', menu=file_menu)

    def open_folder(self):
        self.selected_folder = Path(filedialog.askdirectory())
        self.available_mp3s = []
        use_ai = messagebox.askyesno('AI?', 'Try and discover using the AI?')

        if use_ai:
            diarized = diarization.diarize_files(list(self.selected_folder.glob('*.mp3')),
                                                 {"Deutsch": Path("all_deu.mp3"), "Englisch": Path("all_eng.mp3")},
                                                 True, True)
            for file, similarity in diarized:
                self.available_mp3s.append([file.name, similarity['Deutsch'] > similarity['Englisch']])
        else:
            for file in self.selected_folder.glob('*.mp3'):
                self.available_mp3s.append([file.name, False])

        self.redraw()

    def redraw(self):
        self.treeview.delete(*self.treeview.get_children())
        for mp3 in self.available_mp3s:
            tags = ('german' if mp3[1] else 'englisch',)
            self.treeview.insert('', tk.END, values=tuple(mp3), tags=tags)

        self.german_count_lbl['text'] = f'German Files: {self.count_german()}'

    def play_audio(self, event: tk.Event):
        for selection in self.treeview.selection():
            cols = self.treeview.item(selection)['values']
            print(self.selected_folder / Path(cols[0]))
            playsound(str(Path(self.selected_folder / cols[0]).absolute()), block=False)

    def mark_german(self, event: tk.Event):
        idx = 0
        for selection in self.treeview.selection():
            cols = self.treeview.item(selection)['values']
            idx = [mp3[0] == cols[0] for mp3 in self.available_mp3s].index(True)

            values = self.available_mp3s[idx]
            self.available_mp3s[idx][1] = not values[1]

        self.redraw()

        child = self.treeview.get_children()[idx]
        self.treeview.focus(child)
        self.treeview.selection_set(child)

    def to_dict(self):
        paths = {}
        for mp3 in self.available_mp3s:
            print(mp3)
            paths[str((Path(self.selected_folder) / mp3[0]).absolute())] = {
                'German': bool(mp3[1])
            }
        return paths

    def export_json(self):
        json.dump(self.to_dict(), Path('out.json').open('w', encoding='utf-8'))

    def count_german(self):
        return sum(int(mp3[1]) for mp3 in self.available_mp3s)


def main():
    root = tk.Tk()
    root.title('Audio Splitter Editor')
    window = MainWindow(root)

    root.mainloop()


if __name__ == '__main__':
    main()
