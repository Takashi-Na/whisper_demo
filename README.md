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

# Usage command line
whisper tmp/rec-3037999527844842.mp4 --language Japanese