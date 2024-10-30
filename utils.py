from moviepy.editor import VideoFileClip
from pydub import AudioSegment


def get_previous_appearances(paragraphs, word, index) -> int:
    """
    Get the number of times a word appears in the paragraphs before the given index.

    Arguments
    ---------
    paragraphs : list[list[str]]
        A list of lists of strings, where each list of strings represents a paragraph.
    word : str
        The word to search for.
    index : int
        The index of the paragraph to stop at.

    Returns
    -------
    int
        The number of times the word appears in the paragraphs before the given index.
    """
    count = 0
    for i in range(index):
        paragraph = paragraphs[i]
        paragraph_str="".join(paragraph)
        count += paragraph_str.count(word)
    return count

def merge_dicts_with_lists(dict1: dict, dict2: dict) -> dict:
    """
    Merge two dictionaries where the values are lists.

    Arguments
    ---------
    dict1 : dict
        The first dictionary to merge.
    dict2 : dict
        The second dictionary to merge.

    Returns
    -------
    dict
        A new dictionary containing the merged values.
    """
    merged = {}
    for key in set(dict1) | set(dict2):  # Union of keys in both dictionaries
        if key in dict1 and key in dict2:
            # If both dictionaries have the key, combine values in a list
            merged[key] = [dict1[key], dict2[key]]
        elif key in dict1:
            merged[key] = dict1[key]
        else:
            merged[key] = dict2[key]
    return merged


def get_audio_from_video(videos_folder: str, audio_folder: str, video_name: str) -> None:
    """
    Get the audio from a video and save it as a .wav file.

    Arguments
    ---------
    video_folder : str
        The path to the folder containing the video file.
    audio_folder : str
        The path to the folder where the audio file will be saved.
    video_name : str
        The name of the video file.

    Returns
    -------
    None
    """
    video_path = videos_folder + video_name
    audio_path = audio_folder + video_name.replace(".mp4", ".wav")
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")  # Save audio as .wav format


def split_in_chunks(audio_folder: str, audio_name:str, chunk_folder: str, chunk_count: int) -> list[str]:
    """
    Split an audio file into chunks of a specified size.

    Arguments
    ---------
    audio_folder: str
        The path to the audio file.
    audio_name: str
        The name of the audio file.
    chunk_folder : str
        The path to the folder where the chunks will be saved.
    chunk_count : int
        The total number of chunks.

    Returns
    -------
    list[str]
        A list of the paths to the chunk files.
    """
    audio = AudioSegment.from_wav(audio_folder + audio_name)
    chunk_length = len(audio) // chunk_count  # length of each chunk in milliseconds

    chunks = []
    for i in range(chunk_count):
        start = i * chunk_length
        end = start + chunk_length
        chunk = audio[start:end]
        temp_str = audio_name.replace(".wav","_")
        chunk_name = f"{chunk_folder}{temp_str}chunk_{i+1}.wav"  # Change file extension if needed
        chunk.export(chunk_name, format="wav")
        chunks.append(chunk_name)

    return chunks
