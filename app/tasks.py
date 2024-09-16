import subprocess
import os
import re
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from app.languages_code import LANGUAGE_SHORTCODE

DetectorFactory.seed = 0

def extract_subtitles(input_dir, output_dir):

    subtitle_files = []
    cmd = ['ffmpeg', '-i', input_dir]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = result.stderr.decode('utf-8')

    global base_name
    base_name = os.path.basename(input_dir).split('.')[0]

    subtitle_streams = re.findall(r'Stream #(\d+:\d+).*Subtitle: (.*?)(?: \((.*?)\))?', output)

    if not subtitle_streams:
        print("No subtitles found in the file.")
        return

    for idx, (stream_id, codec, lang_code) in enumerate(subtitle_streams, start=1):
        if not lang_code:
            lang_code = f"{idx}"
        
        output_file = os.path.join(output_dir, f"{base_name}_{lang_code}.srt")
        
        extract_cmd = [
            'ffmpeg',
            '-i', input_dir,
            '-map', stream_id,
            '-c:s', 'srt' if 'utf8' in codec.lower() else 'copy',
            output_file
        ]

        subprocess.run(extract_cmd)

    subtitle_files = convert_srt_to_vtt_and_rename(output_dir)
    return subtitle_files

def convert_srt_to_vtt_and_rename(output_dir):
    vtt_files = []

    for filename in os.listdir(output_dir):
        if filename.endswith(".srt"):
            srt_file = os.path.join(output_dir, filename)
            vtt_file = os.path.join(output_dir, filename.replace(".srt", ".vtt"))

            convert_cmd = ['ffmpeg', '-i', srt_file, vtt_file]
            subprocess.run(convert_cmd)

            try:
                with open(srt_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                    lang_code = detect(content)
                    lang_code = LANGUAGE_SHORTCODE().get(lang_code, 'unknown')
            except (LangDetectException, Exception) as e:
                print(f"Error detecting language: {e}")
                lang_code = "unknown"

            new_vtt_file = os.path.join(output_dir, f"{base_name}_{lang_code}.vtt")
            os.rename(vtt_file, new_vtt_file)
            os.remove(srt_file)

            print(f"Converted and renamed subtitle: {new_vtt_file}")
            vtt_files.append(new_vtt_file)

    return vtt_files