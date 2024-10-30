from faster_whisper import WhisperModel
import torch
from wtpsplit import SaT
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
from concurrent.futures import ProcessPoolExecutor, as_completed
import timeit
from utils import merge_dicts_with_lists, get_previous_appearances, get_audio_from_video, split_in_chunks

# Load Whisper model
whisper_model = WhisperModel("large-v3",
                              device="cuda" if torch.cuda.is_available() else "cpu",
                              compute_type="float32",
                            )

def get_transcript(audio_path: str) -> tuple[str, dict]:
    """
    Get the transcript of a audio and split it into paragraphs.

    Arguments
    ---------
    audio_path : str
        The path to the audio file.

    Returns
    -------
    tuple[str, dict]
        A tuple containing the transcript and a dictionary of word timestamps.
    """

    # Call the Whisper transcribe function on the audio file
    initial_prompt = "Use punctuation, like this."
    segments, _ = whisper_model.transcribe(audio_path,  initial_prompt=initial_prompt, language="en",word_timestamps=True)
    segments = [s for s in segments]

    # Get the transcript and split it into paragraphs
    transcript=""
    word_timestamps={}
    for s in segments:
        transcript+=s.text+""
        for w in s.words:
            word=w.word.strip()
            if word not in word_timestamps:
                word_timestamps[word] = []
            word_timestamps[word].append(w.start)

    return transcript, word_timestamps


def get_paragraphs(transcript: str,word_timestamps: dict) -> list[str]:
    """
    Split a transcript into paragraphs.

    Arguments
    ---------
    transcript : str
        The transcript to split into paragraphs.
    word_timestamps : dict
        A dictionary containing the sorted end timestamps for each word in the transcript.

    Returns
    -------
    list[str]
        A list of paragraphs.
    """
    sat = SaT("sat-3l")
    print("Loaded SaT model.")
    paragraphs = sat.split(transcript, do_paragraph_segmentation=True)
    print("Split transcript into paragraphs:")
    print(paragraphs)
    print(" ")

    # Find the end timestamps for each paragraph
    paragraphs_timestamps = {}
    for index, p in enumerate(paragraphs):
        # Get the last word of the paragraph
        paragraph_str="".join(p)
        last_word = paragraph_str.split()[-1]
        # Get the timestamp of the last word
        last_word_timestamps = word_timestamps[last_word]
        # Find the timestamp of the last word in the video
        count = get_previous_appearances(paragraphs, last_word, index)
        timestamp= last_word_timestamps[count]
        paragraphs_timestamps[timestamp] = p

    print("Paragraphs with timestamps:")
    print(paragraphs_timestamps)
    print(" ")
    return paragraphs_timestamps


def get_scenes(videos_folder: str,video_name: str) -> list[float]:
    """
    Detect the scenes in a video and split it into clips.

    Arguments
    ---------
    video_folder : str
        The path to the folder containing the video file.
    video_name : str
        The name of the video file.

    Returns
    -------
    list[float]
        A list of the end timestamps of the scenes.
    """

    video_path = videos_folder + video_name
    scene_list = detect(video_path, AdaptiveDetector())
    scene_end_seconds = [scene[1].get_seconds() for scene in scene_list]
    return scene_end_seconds


def process_transcript_with_chunks():
    # Assuming get_audio_from_video, split_in_chunks, get_transcript, and merge_dicts_with_lists are defined
    # get_audio_from_video("videos/", "audio/", "ea08cbd8-2524-4883-953e-85d50eca33a6.mp4")

    chunks = split_in_chunks("audio/", "ea08cbd8-2524-4883-953e-85d50eca33a6.wav", "chunks/", 5)
    full_transcript = ""
    full_word_timestamps = {}
    for i, chunk in enumerate(chunks):
        transcript, word_timestamps = get_transcript(chunk)
        print(f"Transcript for chunk {i+1}:")
        print(transcript)
        print(f"Word timestamps for chunk {i+1}:")
        print(word_timestamps)
        print(" ")

        full_transcript += transcript
        full_word_timestamps = merge_dicts_with_lists(full_word_timestamps, word_timestamps)


def process_transcript_with_chunks_parallel():
    # Assuming get_audio_from_video, split_in_chunks, get_transcript, and merge_dicts_with_lists are defined
    # get_audio_from_video("videos/", "audio/", "ea08cbd8-2524-4883-953e-85d50eca33a6.mp4")

    # Split audio into chunks
    chunks = split_in_chunks("audio/", "ea08cbd8-2524-4883-953e-85d50eca33a6.wav", "chunks/", 5)

    full_transcript = ""
    full_word_timestamps = {}

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor() as executor:
        # Submit all tasks to the pool, along with the index for each chunk
        futures = {executor.submit(get_transcript, chunk): i for i, chunk in enumerate(chunks)}

        # Collect results in a list to keep track of their original order
        results = [None] * len(chunks)

        for future in as_completed(futures):
            i = futures[future]  # Retrieve the original index of this chunk
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaa")
            transcript, word_timestamps = future.result()
            results[i] = (transcript, word_timestamps)  # Store results in their original order

    # Now process results in order
    for i, (transcript, word_timestamps) in enumerate(results):
        print(f"Transcript for chunk {i+1}:")
        print(transcript)
        print(f"Word timestamps for chunk {i+1}:")
        print(word_timestamps)
        print(" ")

        # Append transcript and word timestamps
        full_transcript += transcript
        full_word_timestamps = merge_dicts_with_lists(full_word_timestamps, word_timestamps)


def process_transcript():
    # Assuming get_audio_from_video, split_in_chunks, get_transcript, and merge_dicts_with_lists are defined
    # get_audio_from_video("videos/", "audio/", "ea08cbd8-2524-4883-953e-85d50eca33a6.mp4")
    get_transcript("audio/ea08cbd8-2524-4883-953e-85d50eca33a6.wav")


if __name__ == "__main__":
    # Measure the execution time
    # execution_time = timeit.timeit(process_transcript_with_chunks, number=1)
    # print(f"Execution time with chunks: {execution_time} seconds")

    # #Measure the execution time
    # execution_time = timeit.timeit(process_transcript, number=1)
    # print(f"Execution time without chunks: {execution_time} seconds")

    chunks = split_in_chunks("audio/", "ea08cbd8-2524-4883-953e-85d50eca33a6.wav", "chunks/", 5)
    full_transcript = ""
    full_word_timestamps = {}
    for i, chunk in enumerate(chunks):
        transcript, word_timestamps = get_transcript(chunk)
        print(f"Transcript for chunk {i+1}:")
        print(transcript)
        print(f"Word timestamps for chunk {i+1}:")
        print(word_timestamps)
        print(" ")

        full_transcript += transcript
        full_word_timestamps = merge_dicts_with_lists(full_word_timestamps, word_timestamps)
    one_go_transcript, one_go_word_timestamps = get_transcript("audio/ea08cbd8-2524-4883-953e-85d50eca33a6.wav")

    # Assert that the results are the same
    if  full_transcript == one_go_transcript:
        print("Transcripts are the same")
    else:
        print("Transcripts are different")
    if full_word_timestamps == one_go_word_timestamps:
        print("Word timestamps are the same")
    else:
        print("Word timestamps are different")

    # After a run in the terminal, the output is:
        # Transcripts are different
        # Word timestamps are different
