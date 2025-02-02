import whisper
import torch
import numpy as np
from pathlib import Path

def test_transcribe(video_path: str):
    print(f"开始测试转录：{video_path}")
    
    # 检查CUDA可用性
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备：{device}")
    
    try:
        # 加载模型
        print("加载Whisper模型(medium)...")
        model = whisper.load_model("medium", device=device)
        
        # 转录视频
        print("开始转录...")
        result = model.transcribe(
            video_path,
            language="zh",
            task="transcribe",
            word_timestamps=True  # 启用词级别时间戳
        )
        
        # 打印结果
        print("\n转录结果：")
        print("-" * 50)
        for i, segment in enumerate(result["segments"], 1):
            avg_logprob = segment.get("avg_logprob", float("-inf"))
            no_speech_prob = segment.get("no_speech_prob", 1.0)
            compression_ratio = segment.get("compression_ratio", 0.0)
            text = segment.get("text", "").strip()
            start = segment["start"]
            end = segment["end"]
            
            print(f"\n片段 {i}:")
            print(f"时间: {start:.2f}s - {end:.2f}s")
            print(f"文本: {text}")
            print(f"对数概率: {avg_logprob:.4f}")
            print(f"置信度: {np.exp(avg_logprob):.4f}")  # 转换为概率值
            print(f"非语音概率: {no_speech_prob:.4f}")
            print(f"压缩率: {compression_ratio:.4f}")
            
            if not text:
                print("警告: 空文本!")
            if avg_logprob < -1.0:  # 使用配置文件中的阈值
                print(f"警告: 低置信度 (logprob: {avg_logprob:.4f} < -1.0)")
            if no_speech_prob > 0.8:
                print(f"警告: 可能是非语音片段 (no_speech_prob: {no_speech_prob:.4f})")
        
        print("\n统计信息：")
        print(f"总片段数: {len(result['segments'])}")
        avg_logprobs = [s.get("avg_logprob", float("-inf")) for s in result["segments"]]
        avg_confidence = np.mean([np.exp(p) for p in avg_logprobs])
        print(f"平均置信度: {avg_confidence:.4f}")
        empty_segments = sum(1 for s in result["segments"] if not s.get("text", "").strip())
        print(f"空文本片段数: {empty_segments}")
        high_no_speech = sum(1 for s in result["segments"] if s.get("no_speech_prob", 1.0) > 0.8)
        print(f"可能的非语音片段数: {high_no_speech}")
        
    except Exception as e:
        print(f"错误：{str(e)}")
        raise

if __name__ == "__main__":
    video_path = r"C:\Users\LINSUISHENG034\Desktop\Douyin\test_videos\00m33s.mp4"
    if not Path(video_path).exists():
        print(f"错误：视频文件不存在：{video_path}")
    else:
        test_transcribe(video_path)