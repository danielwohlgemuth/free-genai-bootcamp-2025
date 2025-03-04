import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
print(TTS().list_models())

# Initialize TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
# tts = TTS("tts_models/ja/kokoro/tacotron2-DDC").to(device)

# List speakers
print(tts.speakers)

# TTS with list of amplitude values as output, clone the voice from `speaker_wav`
# wav = tts.tts(
#   text="彼は毎朝ジョギんごをして体を健康に保っています",
#   speaker_wav="ja.wav", # ja.wav downloaded from https://myshell-public-repo-host.s3.amazonaws.com/myshellttsbase/examples/jp/JP/speed_1.0/sent_000.wav
#   language="ja"
# )

# # TTS to a file, use a preset speaker for xtts_v2
speakers = ["Chandra MacFarland", "Alexandra Hisakawa", "Zacharie Aimilios", "Uta Obando"]
for speaker in speakers:
    tts.tts_to_file(
        text="こんにちは！田中宏です。日本の東京出身です。ソフトウェアエンジニアとして働いていて、Webアプリケーションの開発が大好きです。暇なときは、アニメを見たり、本を読んだり、新しいラーメン屋を試したりするのが好きです。よろしくお願いします！",
        speaker=speaker,
        language="ja",
        file_path=f"output-xtts_v2-{speaker}.wav"
    )

# TTS to a file for tacotron2-DDC
# tts.tts_to_file(
#     text="こんにちは！田中宏です。日本の東京出身です。ソフトウェアエンジニアとして働いていて、Webアプリケーションの開発が大好きです。暇なときは、アニメを見たり、本を読んだり、新しいラーメン屋を試したりするのが好きです。よろしくお願いします！",
#     file_path=f"output-tacotron2-DDC.wav"
# )
