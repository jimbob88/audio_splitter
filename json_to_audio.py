import argparse
import json
import pathlib
import typing
from pathlib import Path
from typing import List, NamedTuple

from pydub import AudioSegment


class Audio(NamedTuple):
    path: Path
    primary: bool


class PrimaryDict(typing.TypedDict):
    """Mirrors export type of `main.py`"""
    is_primary: bool


def dict_to_grouped_audio(primary_dict: typing.Dict[str, PrimaryDict]):
    """Groups the audio files into their respective groups

    For example if you have two primary audio files (A.mp3 and B.mp3) they will be combined
    into one list [A.mp3, B.mp3].
    """
    files: List[List[Audio]] = []

    for path, prop in primary_dict.items():
        path = Path(path)
        audio = Audio(path, prop['is_primary'])
        if not files or files[-1][0].primary != audio.primary:
            files.append([audio])
        else:
            files[-1].append(audio)
    return files


def concat_audios(files: List[Path], output_path: Path):
    segments = [AudioSegment.from_file(file, file.suffix.lstrip('.')) for file in files]
    total = sum(segments)
    total.export(output_path, format=output_path.suffix.lstrip('.'))


def get_args():
    parser = argparse.ArgumentParser(description="Concatenates mp3 files using a JSON file")
    parser.add_argument('-j', '--json', required=True, type=pathlib.Path, dest='json', help='The json file to convert')
    parser.add_argument('-o', '--out', default=Path('.'), type=pathlib.Path, dest='out_folder', help='The folder '
                                                                                                     'to write to')
    return parser.parse_args()


def main():
    args = get_args()
    dataset: typing.Dict[str, PrimaryDict] = json.load(args.json.open('r', encoding='utf-8'))

    files = dict_to_grouped_audio(dataset)

    pri = 0
    sec = 0
    for audios in files:
        if audios[0].primary:
            pri += 1
            out_file = args.out_folder / Path(f'out_pri{pri:05d}.mp3')
        else:
            sec += 1
            out_file = args.out_folder / Path(f'out_sec{sec:05d}.mp3')
        print(f'Writing {out_file}')
        concat_audios([audio.path for audio in audios], out_file)

    return 0


if __name__ == '__main__':
    main()
