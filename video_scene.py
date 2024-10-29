from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
scene_list = detect('videos/ea08cbd8-2524-4883-953e-85d50eca33a6.mp4', AdaptiveDetector())
split_video_ffmpeg('videos/ea08cbd8-2524-4883-953e-85d50eca33a6.mp4', scene_list, output_dir='stiri/', )