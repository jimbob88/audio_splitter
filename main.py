import json
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List

from playsound import playsound

import diarization


def create_diarized_table(folder: Path, primary_language_training_data: Path, secondary_language_training_data: Path):
    """Creates a table with primary language model

    :param folder: Where to search for mp3 files
    :param primary_language_training_data: A training file [mp3 file containing examples of person speaking]
    :param secondary_language_training_data:  A training file for secondary lang [mp3 containing examples of 2nd person]
    :return: A list of [the audio file name: str, is_primary_language: bool]
    :rtype: list[list[Union[str, bool]]]

    """
    diarized = diarization.diarize_files(list(folder.glob('*.mp3')),
                                         {"Primary": primary_language_training_data,
                                          "Secondary": secondary_language_training_data},
                                         True, True)
    return [[file.name, similarity['Primary'] > similarity['Secondary']] for file, similarity in diarized]


class MainWindow(tk.Frame):
    master: tk.Tk

    def __init__(self, master: tk.Tk = None):
        super().__init__(master)

        self.config = json.load(Path('config.json').open())

        column_names = {
            'file_name': 'File Name',
            'primary': self.config['primary_lang_alias'],
        }

        self.treeview = ttk.Treeview(self.master, columns=tuple(column_names.keys()), show='headings')

        for column, header in column_names.items():
            self.treeview.heading(column, text=header)

        self.treeview.grid(row=0, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscroll=scrollbar.set)
        self.treeview.tag_configure('primary', background='grey')
        self.treeview.tag_configure('secondary', background='orange')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.german_count_lbl = tk.Label(self.master, text='Primary Count: ')
        self.german_count_lbl.grid(row=1, column=0, columnspan=1, sticky='ew')

        self._configure_menubar()
        self._configure_key_bindings()

        self.available_mp3s: List[List] = []
        self.selected_folder = Path('.').absolute()

    def _configure_key_bindings(self):
        self.treeview.bind('<space>', self.play_audio)
        self.treeview.bind('d', self.mark_primary)

    def _configure_menubar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Open Folder', command=self.open_folder)
        file_menu.add_command(label='Export JSON', command=self.export_json)

        menubar.add_cascade(label='File', menu=file_menu)

    def open_folder(self):
        self.selected_folder = Path(filedialog.askdirectory())
        use_ai = messagebox.askyesno('AI?', 'Try and discover using the AI [diarization]?')

        if use_ai:
            self.available_mp3s = create_diarized_table(self.selected_folder,
                                                        Path(self.config["primary_language_training_data"]),
                                                        Path(self.config["secondary_language_training_data"]))
        else:
            self.available_mp3s = [[file.name, False] for file in self.selected_folder.glob('*.mp3')]

        self.redraw()

    def redraw(self):
        self.treeview.delete(*self.treeview.get_children())
        for mp3 in self.available_mp3s:
            tags = ('primary' if mp3[1] else 'secondary',)
            self.treeview.insert('', tk.END, values=tuple(mp3), tags=tags)

        self.german_count_lbl['text'] = f'Primary Files: {self.count_primary()}'

    def play_audio(self, event: tk.Event):
        for selection in self.treeview.selection():
            cols = self.treeview.item(selection)['values']
            print(self.selected_folder / Path(cols[0]))
            playsound(str(Path(self.selected_folder / cols[0]).absolute()), block=False)

    def mark_primary(self, event: tk.Event):
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
            path = str((Path(self.selected_folder) / mp3[0]).absolute())
            paths[path] = {
                'is_primary': bool(mp3[1])
            }
        return paths

    def export_json(self):
        """Converts the dict representation into a json file [filename defined in config.json]"""
        file = Path(self.config["default_out_filename"]).open('w', encoding='utf-8')
        json.dump(self.to_dict(), file)

    def count_primary(self):
        """Calculates how many primary values there are

        This works by ignoring any values that are marked as joined
        """
        count = 0
        for idx, mp3 in enumerate(self.available_mp3s):
            if mp3[1] and (idx == 0 or not self.available_mp3s[-1][1]):
                count += 1
        return count


def main():
    root = tk.Tk()
    root.title('Audio Splitter Editor')
    window = MainWindow(root)

    root.mainloop()


if __name__ == '__main__':
    main()
