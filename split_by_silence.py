import argparse
from pathlib import Path

from pydub import AudioSegment
from pydub.silence import split_on_silence


def get_args():
    parser = argparse.ArgumentParser(description="Split an mp3 file by silence")
    parser.add_argument('-f', '--file', type=Path, required=True, help="File to slit")
    parser.add_argument('-m', '--min_silence_len', type=int, default=400,
                        help="Minimum length of silence to split at (ms)")
    parser.add_argument('-s', '--silence_threshold', type=int, default=-48,
                        help="At what db should it be considered silent")
    parser.add_argument('-k', '--keep_silence', type=int, default=200,
                        help="How much silence should be left on either side (ms)")
    parser.add_argument('-o', '--out_folder', type=Path, default=Path('.'),
                        help="Where to save the new files to")
    return parser.parse_args()


# https://stackoverflow.com/a/46001755/5210078
def main():
    args = get_args()

    song = AudioSegment.from_file(args.file, format=args.file.suffix.strip('.'))

    chunks = split_on_silence(
        song,
        min_silence_len=args.min_silence_len,
        silence_thresh=args.silence_threshold,
        keep_silence=args.keep_silence
    )
    print(chunks)

    for i, chunk in enumerate(chunks, start=1):
        silence_chunk = AudioSegment.silent(duration=500)
        audio_chunk = silence_chunk + chunk + silence_chunk
        fname = args.out_folder / f"integration_2.3({i:03}).mp3"
        print(f"Exporting {fname}, {chunk.frame_rate}")
        audio_chunk.export(fname, bitrate="192k", format="mp3")


if __name__ == '__main__':
    main()
