"""Build Take an Interview practice audio and exam-style timer videos from a set file.

Usage: make_practice_set.py <set.txt> <out_dir> <name> [--voice af_heart] [--no-video]

set.txt: line 1 = the interviewer's intro, then one question per line, optionally a last line "OUTRO: ...".
Writes <name>-full.m4a/.mp4 (intro + all questions) and <name>-q<N>.m4a/.mp4 (one question each).
Each question: question audio, 0.6 s, start beep (880 Hz), 45 s answer window, double end beep (660 Hz).
The video shows a 00:45 countdown that turns orange in the last 10 s.
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import ffmpeg, wav_seconds  # noqa: E402
from tts import synthesize  # noqa: E402

ANSWER_SECS = 45
W, H = 1280, 720
BG, HEADER, CARD, BORDER = "#EEF1F5", "#22344A", "#FFFFFF", "#D5DBE3"
INK, MUTED, IDLE = "#22344A", "#6B7787", "#A3ADBA"
BLUE, ORANGE, RED, GREEN, TRACK = "#2563EB", "#C2410C", "#B42318", "#15803D", "#E3E8EF"
FONTS = {
    False: ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"],
    True: ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"],
}


def font(size, bold=False):
    for path in FONTS[bold]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ---------- audio ----------

def build_audio(set_file, voice, work, out_dir, name):
    lines = [l.strip() for l in Path(set_file).read_text().splitlines() if l.strip()]
    intro = lines[0]
    outro = next((l[6:].strip() for l in lines if l.startswith("OUTRO:")), "That's the end of the interview.")
    questions = [l for l in lines[1:] if not l.startswith("OUTRO:")]

    raw = [(work / "intro_raw.wav", intro), (work / "outro_raw.wav", outro)]
    raw += [(work / f"q{i}_raw.wav", q) for i, q in enumerate(questions, 1)]
    synthesize(voice, raw)
    for path, _ in raw:
        ffmpeg("-i", str(path), "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(path).replace("_raw", ""))

    def silence(secs, out):
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(secs), "-c:a", "pcm_s16le", str(work / out))

    def tone(freq, secs, out):
        ffmpeg("-f", "lavfi", "-i", f"sine=frequency={freq}:duration={secs}:sample_rate=44100",
               "-af", f"volume=0.35,afade=t=in:d=0.02,afade=t=out:st={secs - 0.04:.2f}:d=0.04",
               "-ac", "1", "-c:a", "pcm_s16le", str(work / out))

    silence(0.6, "gap_short.wav")
    silence(1.2, "gap_mid.wav")
    silence(3, "gap_long.wav")
    silence(ANSWER_SECS, "answer.wav")
    silence(0.12, "b_gap.wav")
    tone(880, 0.35, "beep_start.wav")
    tone(660, 0.18, "b1.wav")
    concat(work, ["b1.wav", "b_gap.wav", "b1.wav"], work / "beep_end.wav", codec=["-c:a", "pcm_s16le"])

    block = lambda i: [f"q{i}.wav", "gap_short.wav", "beep_start.wav", "answer.wav", "beep_end.wav"]
    full = ["intro.wav", "gap_mid.wav"]
    for i in range(1, len(questions) + 1):
        concat(work, block(i), out_dir / f"{name}-q{i}.m4a")
        full += block(i) + ["gap_long.wav"]
    concat(work, full + ["outro.wav"], out_dir / f"{name}-full.m4a")
    return len(questions)


def concat(work, parts, out, codec=("-c:a", "aac", "-b:a", "128k")):
    listing = work / (Path(out).name + ".txt")
    listing.write_text("".join(f"file '{work / p}'\n" for p in parts))
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), *codec, str(out))


# ---------- video ----------

def avatar(speaking):
    size = 260
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((0, 0, size, size), fill="#C9D3DF")
    d.ellipse((size / 2 - 48, 58, size / 2 + 48, 154), fill="#8A9AB0")
    d.ellipse((size / 2 - 100, 170, size / 2 + 100, 380), fill="#8A9AB0")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size + 24, size + 24), (0, 0, 0, 0))
    out.paste(layer, (12, 12), mask)
    if speaking:
        ImageDraw.Draw(out).ellipse((2, 2, size + 21, size + 21), outline=BLUE, width=7)
    return out


def render(state, num_q, frames):
    phase, q, remaining = state
    path = frames / f"{phase}_{q}_{remaining}.png"
    if path.exists():
        return path
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_status, f_label, f_small = font(34, True), font(20, True), font(16)
    f_timer, f_name, f_big = font(132, True), font(22), font(64, True)

    d.rectangle((0, 0, W, 72), fill=HEADER)
    d.text((40, 36), "Speaking  ·  Take an Interview", font=font(26, True), fill="white", anchor="lm")
    right = {"intro": "Introduction", "end": "Complete"}.get(phase, f"Question {q} of {num_q}")
    d.text((W - 40, 36), right, font=font(24), fill="white", anchor="rm")
    d.rounded_rectangle((70, 110, W - 70, 650), radius=18, fill=CARD, outline=BORDER, width=2)
    d.line((560, 150, 560, 610), fill=BORDER, width=2)

    speaking = phase in ("intro", "listen", "end")
    av = avatar(speaking)
    img.paste(av, (315 - av.width // 2, 330 - av.height // 2), av)
    d.text((315, 500), "Interviewer", font=f_name, fill=MUTED, anchor="mm")
    if speaking:
        for i, h in enumerate((14, 26, 18, 30, 16)):
            d.rounded_rectangle((268 + i * 20, 545 - h / 2, 278 + i * 20, 545 + h / 2), radius=4, fill=BLUE)

    cx = 880
    status, color, dot = {
        "intro": ("Listen to the interviewer", INK, None),
        "listen": ("Listen to the question", INK, None),
        "answer": ("Answer now", GREEN, GREEN),
        "timeup": ("Time is up", RED, None),
        "end": ("End of interview", INK, None),
    }[phase]
    if dot:
        tw = d.textlength(status, font=f_status)
        d.ellipse((cx - tw / 2 - 34, 192, cx - tw / 2 - 12, 214), fill=dot)
        d.text((cx + 6, 203), status, font=f_status, fill=color, anchor="mm")
    else:
        d.text((cx, 203), status, font=f_status, fill=color, anchor="mm")

    if phase in ("listen", "answer", "timeup"):
        if phase == "listen":
            shown, tcolor, frac, bar_color = ANSWER_SECS, IDLE, 1.0, IDLE
        elif phase == "answer":
            shown, frac = remaining, remaining / ANSWER_SECS
            tcolor = bar_color = ORANGE if remaining <= 10 else INK
            bar_color = ORANGE if remaining <= 10 else BLUE
        else:
            shown, tcolor, frac, bar_color = 0, RED, 0.0, RED
        d.text((cx, 290), "RESPONSE TIME", font=f_label, fill=MUTED, anchor="mm")
        d.text((cx, 390), f"00:{shown:02d}", font=f_timer, fill=tcolor, anchor="mm")
        bar = (cx - 230, 478, cx + 230, 494)
        d.rounded_rectangle(bar, radius=8, fill=TRACK)
        if frac > 0:
            d.rounded_rectangle((bar[0], bar[1], bar[0] + (bar[2] - bar[0]) * frac, bar[3]), radius=8, fill=bar_color)
        hint = {"listen": "The timer starts after the beep.", "answer": "Keep talking until the time runs out.",
                "timeup": "Stop speaking."}[phase]
        d.text((cx, 545), hint, font=f_name, fill=MUTED, anchor="mm")
    elif phase == "intro":
        d.text((cx, 330), f"{num_q} questions", font=f_big, fill=INK, anchor="mm")
        d.text((cx, 400), f"{ANSWER_SECS} seconds per answer, no preparation time", font=f_name, fill=MUTED, anchor="mm")
    else:
        d.text((cx, 330), "Well done.", font=f_big, fill=INK, anchor="mm")
        d.text((cx, 400), "Stop your recording now.", font=f_name, fill=MUTED, anchor="mm")

    d.text((40, H - 30), "Practice simulation. Not an official ETS product.", font=f_small, fill=IDLE, anchor="lm")
    img.save(path)
    return path


def question_block(work, q, tail):
    yield ("listen", q, 0), wav_seconds(work / f"q{q}.wav") + wav_seconds(work / "gap_short.wav")
    yield ("answer", q, ANSWER_SECS), wav_seconds(work / "beep_start.wav") + 1.0
    for remaining in range(ANSWER_SECS - 1, 0, -1):
        yield ("answer", q, remaining), 1.0
    yield ("timeup", q, 0), wav_seconds(work / "beep_end.wav") + tail


def build_video(timeline, audio, out, num_q, work):
    frames = work / "frames"
    frames.mkdir(exist_ok=True)
    listing = work / (out.name + ".txt")
    with open(listing, "w") as f:
        for state, duration in timeline:
            last = render(state, num_q, frames)
            f.write(f"file '{last}'\nduration {duration:.4f}\n")
        f.write(f"file '{last}'\n")
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-i", str(audio), "-vf", "fps=25,format=yuv420p",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "stillimage", "-c:a", "copy",
           "-shortest", "-movflags", "+faststart", str(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set_file")
    ap.add_argument("out_dir")
    ap.add_argument("name")
    ap.add_argument("--voice", default="af_heart")
    ap.add_argument("--no-video", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        n = build_audio(args.set_file, args.voice, work, out_dir, args.name)
        if not args.no_video:
            full = [(("intro", 0, 0), wav_seconds(work / "intro.wav") + wav_seconds(work / "gap_mid.wav"))]
            for q in range(1, n + 1):
                full += list(question_block(work, q, tail=wav_seconds(work / "gap_long.wav")))
            full.append((("end", 0, 0), wav_seconds(work / "outro.wav") + 0.5))
            build_video(full, out_dir / f"{args.name}-full.m4a", out_dir / f"{args.name}-full.mp4", n, work)
            for q in range(1, n + 1):
                build_video(list(question_block(work, q, tail=0.0)), out_dir / f"{args.name}-q{q}.m4a",
                            out_dir / f"{args.name}-q{q}.mp4", n, work)
    print(f"built {n} questions into {out_dir}")


if __name__ == "__main__":
    main()
