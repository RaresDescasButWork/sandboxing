from faster_whisper import WhisperModel
import torch 
from moviepy.editor import VideoFileClip
from wtpsplit import SaT
from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg

# Load Whisper model
whisper_model = WhisperModel("large-v3",
                              device="cuda" if torch.cuda.is_available() else "cpu",
                              compute_type="float32",
                            )

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
    """
    count = 0
    for i in range(index):
        paragraph = paragraphs[i]
        paragraph_str="".join(paragraph)
        count += paragraph_str.count(word)
    return count


def get_transcript_paragraphs(videos_folder: str, audio_folder: str, video_name: str):
    """
    Get the transcript of a video and split it into paragraphs.

    Arguments
    ---------
    video_folder : str
        The path to the folder containing the video file.
    audio_folder : str
        The path to the folder where the audio file will be saved.
    video_name : str
        The name of the video file.
    """

    # Get the audio from the video
    video_path = videos_folder + video_name
    audio_path = audio_folder + video_name.replace(".mp4", ".wav")
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")  # Save audio as .wav format

    # Call the Whisper transcribe function on the audio file
    initial_prompt = "Use punctuation, like this."
    segments, _ = whisper_model.transcribe(audio_path,  initial_prompt=initial_prompt, language="en",word_timestamps=True)
    segments = [s for s in segments]
    
    # Get the transcript and split it into paragraphs
    transcript=""
    word_timestamps={}
    for s in segments:
        text=s.text
        transcript+=text+"" 

        for w in s.words:
            word=w.word.strip()
            if word not in word_timestamps:
                word_timestamps[word] = []
            word_timestamps[word].append(w.start)

    # Split into paragraphs
    sat = SaT("sat-3l")
    print("Loaded SaT model.")
    paragraphs = sat.split(transcript, do_paragraph_segmentation=True)
    print("Split transcript into paragraphs:")
    print(paragraphs)
    print(" ")

    import pdb; pdb.set_trace()
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
    

def get_scenes(videos_folder: str,video_name: str) -> list[float]:
    """
    Detect the scenes in a video and split it into clips.

    Arguments
    ---------
    video_folder : str
        The path to the folder containing the video file.
    video_name : str
        The name of the video file.
    """

    video_path = videos_folder + video_name
    scene_list = detect(video_path, AdaptiveDetector())
    scene_end_seconds = [scene[1].get_seconds() for scene in scene_list]
    return scene_end_seconds


if __name__ == "__main__":
    get_transcript_paragraphs(videos_folder="videos/",video_name="ea08cbd8-2524-4883-953e-85d50eca33a6.mp4",audio_folder="audio/")
    # get_scenes("videos/","ea08cbd8-2524-4883-953e-85d50eca33a6.mp4")