import json
from pathlib import Path
from typing import List, NamedTuple

from pydub import AudioSegment

dataset = json.load(Path('out.json').open('r', encoding='utf-8'))


class Audio(NamedTuple):
    path: Path
    primary: bool


files: List[List[Audio]] = []

for path, prop in dataset.items():
    path = Path(path)
    audio = Audio(path, prop['Primary'])
    if not files or files[- 1][0].primary != prop['Primary']:
        files.append([audio])
    else:
        files[-1].append(audio)


def concat_audios(files: List[Path], output_path: Path):
    segments = [AudioSegment.from_file(file, file.suffix.lstrip('.')) for file in files]
    total = sum(segments)
    total.export(output_path, format=output_path.suffix.lstrip('.'))


pri = 0
sec = 0
for audios in files:
    if audios[0].primary:
        pri += 1
        concat_audios([audio.path for audio in audios], Path(f'out_pri{pri:05d}.mp3'))
    else:
        sec += 1
        concat_audios([audio.path for audio in audios], Path(f'out_sec{sec:05d}.mp3'))
