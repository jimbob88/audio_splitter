from pathlib import Path
from typing import Dict, List, Union, Tuple, Generator

import numpy as np
from resemblyzer import preprocess_wav, VoiceEncoder


def embed_speakers(
        wav_paths: Dict[str, Path], encoder: VoiceEncoder
) -> Dict[str, float]:
    """Given a dict of wavs, returns a dict of speaker embeddings"""
    wavs = {name: preprocess_wav(wav) for name, wav in wav_paths.items()}

    return {name: encoder.embed_utterance(wav) for name, wav in wavs.items()}


def similarity(
        wav: np.ndarray, encoder: VoiceEncoder, speaker_embeds: Dict[str, float]
) -> Dict[str, np.ndarray]:
    """Calculates how similar (at a constant rate) each section of an audio file is to a speaker"""
    _, cont_embeds, wav_splits = encoder.embed_utterance(
        wav, return_partials=True, rate=16
    )
    return {
        name: cont_embeds @ speaker_embed
        for name, speaker_embed in speaker_embeds.items()
    }


def sim(wav: Path, wav_paths: Dict[str, Path], average: bool = False):
    enc = VoiceEncoder("cpu")

    wav = preprocess_wav(wav)
    speaker_embeds = embed_speakers(wav_paths, enc)

    similarity_dict = similarity(wav, enc, speaker_embeds)
    if average:
        return {
            name: np.mean(probabilities)
            for name, probabilities in similarity_dict.items()
        }
    return similarity_dict


def diarize_files(paths: List[Path], speaker_paths: Dict[str, Path], average=True, progress=False) -> Generator[
    Tuple[Path, Dict[str, Union[np.ndarray, float]]], None, None]:
    enc = VoiceEncoder("cpu")
    speaker_embeds = embed_speakers(speaker_paths, enc)

    for idx, wav_path in enumerate(paths):
        if progress:
            print(f"{(idx / len(paths)) * 100:.1f}%")
        wav = preprocess_wav(wav_path)
        similarity_dict = similarity(wav, enc, speaker_embeds)
        if average:
            similarity_dict = {
                name: np.mean(probabilities)
                for name, probabilities in similarity_dict.items()
            }

        yield wav_path, similarity_dict


def main():
    similarity_dict = sim(
        Path("1.1.wav"),
        {"Deutsch": Path("all_deu.mp3"), "Englisch": Path("all_eng.mp3")},
        True,
    )
    print(similarity_dict)


if __name__ == "__main__":
    main()
