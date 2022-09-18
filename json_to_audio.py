import json
from pathlib import Path
from typing import List, NamedTuple

from pydub import AudioSegment

dataset = json.load(Path('out.json').open('r', encoding='utf-8'))


class Audio(NamedTuple):
    path: Path
    german: bool


files: List[List[Audio]] = []

for path, prop in dataset.items():
    path = Path(path)
    audio = Audio(path, prop['German'])
    if files:
        if files[-1][0].german == prop['German']:
            files[-1].append(audio)
        else:
            files.append([audio])
    else:
        files.append([audio])


def concat_audios(files: List[Path], output_path: Path):
    print([file.suffix.lstrip('.') for file in files])
    audios = [AudioSegment.from_file(file, file.suffix.lstrip('.')) for file in files]
    total = sum(audios)
    total.export(output_path, format=output_path.suffix.lstrip('.'))


eng = 0
deu = 0
for audios in files:
    if audios[0].german:
        deu += 1
        concat_audios([audio.path for audio in audios], Path(f'out_deu{deu:05d}.mp3'))
    else:
        eng += 1
        concat_audios([audio.path for audio in audios], Path(f'out_eng{eng:05d}.mp3'))
