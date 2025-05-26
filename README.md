# 目的

# setup
https://github.com/openai/whisper 参照

pyenv local 3.12.3

brew install portaudio

pip install -U \
    openai-whisper \
    pyaudio \
    numpy

brew insntall ffmpeg
ffmpeg version

> ffmpeg version 7.1.1 Copyright (c) 2000-2025 the FFmpeg developers

# Usage whisper from command line
映像データから文字起こしする標準的な使い方ができる
whisper tmp/rec-3037999527844842.mp4 --language Japanese

# Usage realtime_whisper.py
`tmp/`ディレクトリ配下に文字起こししたいデータ(mp4, mp3, wav等)を配置
`realtime_whisper.py`のfile_nameにファイル名を設定

CLIから
python realtime_whisper.py
を実行
