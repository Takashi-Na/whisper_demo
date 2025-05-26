import numpy as np
import whisper
import time
import subprocess
import threading
import queue
from datetime import datetime, timedelta

# 音声入力の設定
CHUNK = 1024
RATE = 16000
RECORD_SECONDS = 15  # 15秒ごとに音声を認識

def process_audio_stream(audio_queue, video_path):
    """FFmpegを使用して動画から音声の標準出力を抽出し、キューに追加"""
    # 動画の長さを取得
    duration_cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    duration = float(subprocess.check_output(duration_cmd).decode().strip())
    
    command = [
        'ffmpeg',
        '-i', video_path,
        '-f', 's16le',  # 16ビットリトルエンディアンPCM
        '-ac', '1',     # モノラル
        '-ar', '16000', # 16kHz
        '-'            # 標準出力に出力
    ]
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 音声データの処理時間を追跡
    processed_samples = 0
    while True:
        # 音声データを読み込み
        audio_data = process.stdout.read(CHUNK * 2)  # 16ビットなので2倍
        if not audio_data:
            break
        
        # NumPy配列に変換
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # 浮動小数点数に正規化
        audio_array = audio_array.astype(np.float32) / 32768.0
        
        # 現在の時間位置を計算（サンプル数から）
        processed_samples += len(audio_array)
        current_time = processed_samples / RATE
        
        # キューに追加（時間情報も含める）
        audio_queue.put((audio_array, current_time))
    
    process.stdout.close()
    process.stderr.close()
    process.wait()

def format_time(seconds):
    """秒数を時:分:秒の形式に変換"""
    return str(timedelta(seconds=int(seconds)))

def process_video_audio(video_path):
    """動画の音声をリアルタイムで処理"""
    # 音声データを格納するキュー
    audio_queue = queue.Queue()
    
    # 音声処理スレッドを開始
    audio_thread = threading.Thread(
        target=process_audio_stream,
        args=(audio_queue, video_path)
    )
    audio_thread.start()
    
    # Whisperモデルの読み込み
    print("Whisperモデルを読み込み中...")
    model = whisper.load_model("base")
    print("モデルの読み込み完了")
    
    # 音声データを蓄積するバッファ
    audio_buffer = []
    time_buffer = []
    buffer_duration = 15  # 15秒分のバッファ
    samples_per_buffer = RATE * buffer_duration  # 15秒分のサンプル数
    
    try:
        while True:
            # キューから音声データを取得
            try:
                audio_chunk, current_time = audio_queue.get(timeout=1)
                audio_buffer.append(audio_chunk)
                time_buffer.append(current_time)
                
                # バッファに蓄積されたサンプル数を計算
                total_samples = sum(len(chunk) for chunk in audio_buffer)
                
                # バッファが15秒分になったら処理
                if total_samples >= samples_per_buffer:
                    # バッファを結合
                    audio_data = np.concatenate(audio_buffer)
                    
                    # 開始時間を取得
                    start_time = time_buffer[0]
                    
                    # Whisperで音声認識
                    result = model.transcribe(audio_data, language="ja", fp16=False)
                    print(f"[{format_time(start_time)}] {result['text']}")
                    
                    # バッファをクリア
                    audio_buffer = []
                    time_buffer = []
                    
            except queue.Empty:
                if not audio_thread.is_alive():
                    break
                continue
            
    except KeyboardInterrupt:
        print("\nプログラムを終了します")

def main():
    # 動画ファイルのパスを指定
    video_path = "tmp/"
    file_name = "rec-3037999527844842.mp4"
    
    # 動画の音声を処理
    process_video_audio(video_path + file_name)

if __name__ == "__main__":
    main()
