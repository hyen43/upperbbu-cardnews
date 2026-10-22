# 카드뉴스 낱장(4:5)을 릴스용 9:16 슬라이드쇼 mp4로 변환
# 사용법: python3 scripts/make_reel.py weeks/2026-10-22 [--music music/xxx.mp3] [--sec 3.2]
# 결과: weeks/.../out/reel.mp4 (음악 없으면 무음 트랙 포함)
import argparse, glob, os, subprocess, tempfile
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument('week')
ap.add_argument('--music')
ap.add_argument('--sec', type=float, default=3.2, help='장당 노출 시간(초), 표지는 2초')
a = ap.parse_args()

slides = sorted(glob.glob(f'{a.week}/out/[0-9][0-9].jpg'))
tmp = tempfile.mkdtemp()
frames = []
for i, p in enumerate(slides):
    card = Image.open(p).convert('RGB')
    # 배경: 같은 카드를 꽉 채워 흐리게 + 어둡게
    bg = card.resize((1536, 1920)).crop((228, 0, 1308, 1920)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new('RGB', bg.size, (0, 0, 0)), 0.35)
    # 카드는 위쪽으로 살짝 올려서 릴스 하단 캡션 UI와 덜 겹치게
    bg.paste(card, (0, 230))
    f = os.path.join(tmp, f'{i:02d}.png')
    bg.save(f)
    frames.append((f, 2.0 if i == 0 else a.sec))

lst = os.path.join(tmp, 'list.txt')
with open(lst, 'w') as fh:
    for f, d in frames:
        fh.write(f"file '{f}'\nduration {d}\n")
    fh.write(f"file '{frames[-1][0]}'\n")  # concat demuxer는 마지막 duration 적용에 한 번 더 필요
total = sum(d for _, d in frames)

out = f'{a.week}/out/reel.mp4'
audio = ['-i', a.music] if a.music else ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, *audio,
       '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
       '-c:a', 'aac', '-b:a', '128k', '-af', f'afade=t=out:st={total - 1.5}:d=1.5',
       '-t', str(total), '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print(out, f'{total:.1f}s')
