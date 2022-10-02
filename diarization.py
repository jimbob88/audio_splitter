from pathlib import Path
from typing import Dict, List, Union, Tuple, Generator

import numpy as np
from resemblyzer import preprocess_wav, VoiceEncoder


def embed_speakers(wav_paths: Dict[str, Path], encoder: VoiceEncoder) -> Dict[str, float]:
    """Given a dict of wavs, returns a dict of speaker embeddings"""
    wavs = {name: preprocess_wav(wav) for name, wav in wav_paths.items()}

    return {name: encoder.embed_utterance(wav) for name, wav in wavs.items()}


def similarity(
        wav: np.ndarray, encoder: VoiceEncoder, speaker_embeds: Dict[str, float]
) -> Dict[str, np.ndarray]:
    """Calculates how similar (at a constant rate) each section of an audio file is to a speaker"""
    _, cont_embeds, wav_splits = encoder.embed_utterance(wav, return_partials=True, rate=16)
    
    return {
        name: cont_embeds @ speaker_embed
        for name, speaker_embed in speaker_embeds.items()
    }


def sim(wav: Path, wav_paths: Dict[str, Path], average: bool = False):
    """Given a wav file, and a training set, calculate the weights for each speaker

    :param wav: The wav file to analyse
    :param wav_paths: The training data [i.e. {'bob': bob_example.mp3, 'jill': jill_example.mp3}]
    :param average: Whether to calculate the mean for each name [if False, gives a list of weights for each segment]
    :return: A dictionary of {name: list[probabilities]} or {name: average_probability}
    :rtype: dict[str, list[float]|float]
    """
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
    """Given a list of wav files and a training dataset, diarizes each file

    :param paths: A list of wav files
    :param speaker_paths: The training dataset i.e. {'dylan': dylan_speaking.mp3, 'jeff': jeff_talking.mp3}
    :param average: If true instead of giving weights per segment, it finds the average for each speaker
    :param progress: Whether to print the current percentage
    """
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
    """A simple example of a use case"""
    similarity_dict = sim(
        Path("1.1.wav"),
        {"Deutsch": Path("all_deu.mp3"), "Englisch": Path("all_eng.mp3")},
        True,
    )
    print(similarity_dict)


if __name__ == "__main__":
    main()
