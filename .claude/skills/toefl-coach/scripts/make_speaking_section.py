"""Build a full Speaking section (Listen and Repeat + Take an Interview) as audio and an exam-style video.

Usage: make_speaking_section.py <section.json> <out_dir>

Follows the ETS Updated TOEFL iBT Test Overview and the Official Guide (2026, pp. 226-234):
- Listen and Repeat: a narrator sets the scene ("... Repeat only once."), then 7 sentences in the fixed pattern
  2 short (9-11 syllables) / 3 medium (14-16) / 2 long (19-23). After each sentence there is a 2-second pause and
  a beep, then 8 s (sentences 1-2), 10 s (3-5) or 12 s (6-7) to repeat. The screen shows an illustration of the
  setting, and a marker moves to the part of it each sentence is about. On-screen line: "Listen and repeat only once."
- Take an Interview: the narrator introduces the situation, then the interviewer asks 4 questions; 45 s each,
  no preparation time. On-screen line: "Please answer the interviewer's questions."
section.json: see speaking/sets/speaking-section-1.json. Optional keys: listen_repeat.scene ("room" draws a floor plan
instead of the campus map); listen_repeat.intro_audio, sentences[].audio, interview.intro_audio, interview.audio (list)
and outro_audio take prerecorded audio or video files (paths relative to the JSON) instead of TTS.
Listen and Repeat drill: "listen_repeat_parts" (a list of listen_repeat blocks, each its own scene and narrator line)
replaces "listen_repeat", and "interview" may be left out; the video then shows "Part n" in the header, as in
speaking/sets/listen-repeat-drill-1.json.
Writes <id>.m4a and <id>.mp4. Every spoken line is checked with Whisper (lines that differ are printed as CHECK).
"""
import json
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _env import ffmpeg  # noqa: E402
from make_listening_test import check  # noqa: E402
from make_practice_set import BG, BLUE, BORDER, CARD, GREEN, HEADER, IDLE, INK, MUTED, ORANGE, RED, TRACK, H, W, avatar, font  # noqa: E402
from tts import synthesize  # noqa: E402

RATE = 24000
INTERVIEW_SECS = 45


LR_PAUSE = 2.0  # Official Guide p. 229: "a 2-second pause followed by an audible beep"


def lr_seconds(index):
    """Response time for Listen and Repeat sentence `index` (0-based): 2 short, 3 medium, 2 long (Official Guide p. 226)."""
    return 8 if index < 2 else 10 if index < 5 else 12


def tone(freq, secs):
    t = np.arange(int(RATE * secs)) / RATE
    env = np.minimum(1, np.minimum(t / 0.02, (secs - t) / 0.04))
    return (0.35 * env * np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)


def silence(secs):
    return np.zeros(int(RATE * secs), dtype=np.int16)


BEEP_START = tone(880, 0.35)
BEEP_END = np.concatenate([tone(660, 0.18), silence(0.12), tone(660, 0.18)])


def read_wav(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


# ---------- frames ----------
F = {k: font(*v) for k, v in {"header": (26, True), "header_r": (24, False), "status": (34, True), "label": (20, True),
                               "timer": (120, True), "small": (16, False), "body": (22, False), "spot": (17, True),
                               "title": (44, True)}.items()}

# Positions of the illustration's places (inside the left panel), in tour order.
SPOTS = [(150, 560), (230, 450), (190, 330), (360, 300), (330, 450), (470, 420), (470, 200)]


def campus(labels, current, scene="campus"):
    """The illustration: a campus map, or with scene="room" a room floor plan where every place is a piece of
    equipment. Visited places are dimmed, the current one is highlighted."""
    room = scene == "room"
    img = Image.new("RGB", (560, 520), "#F4EEE4" if room else "#E8F2E1")
    d = ImageDraw.Draw(img)
    pts = [(x - 70, y - 110) for x, y in SPOTS]
    if room:
        d.rectangle((10, 10, 549, 509), outline="#B9AE9C", width=6)
    else:
        d.line(pts, fill="#F3E3C3", width=26, joint="curve")
        d.ellipse((pts[1][0] - 26, pts[1][1] - 26, pts[1][0] + 26, pts[1][1] + 26), fill="#9CC9E8", outline="#6FA8D0", width=3)
    for i, ((x, y), label) in enumerate(zip(pts, labels)):
        if not room and i in (0, 1, 4):  # gate, fountain and lawn are open spaces, the rest are buildings
            if i == 4:
                d.rounded_rectangle((x - 60, y - 34, x + 60, y + 34), radius=12, fill="#BFE0A8")
        else:
            hw = 44 if room else 58  # narrower in a room, where places 2 and 5 sit side by side
            d.rounded_rectangle((x - hw, y - 36, x + hw, y + 36), radius=8, fill="#D9DEE6", outline="#AEB7C4", width=2)
        visited, now = i < current, i == current
        color = BLUE if now else ("#9AA5B4" if visited else "#55657A")
        r = 17 if now else 13
        d.ellipse((x - r, y - r, x + r, y + r), fill=color, outline="white", width=3)
        d.text((x, y), str(i + 1), font=F["small"], fill="white", anchor="mm")
        d.text((x, y + 46 if i != 6 else y - 50), label, font=F["spot"], fill=INK if now else MUTED, anchor="mm")
        if now:
            d.ellipse((x - 30, y - 30, x + 30, y + 30), outline=BLUE, width=4)
    return img


def lr_parts(section):
    return section.get("listen_repeat_parts") or [section["listen_repeat"]]


def frame(state, section, frames_dir):
    kind, idx, remaining, part = (*state, 0) if len(state) == 3 else state
    path = frames_dir / f"{kind}_{part}_{idx}_{remaining}.png"
    if path.exists():
        return path
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 72), fill=HEADER)
    parts = lr_parts(section)
    lr = parts[part]
    n_lr, n_iv = len(lr["sentences"]), len(section.get("interview", {}).get("questions", []))
    task = "Listen and Repeat" if kind.startswith("lr") else "Take an Interview" if kind.startswith("iv") else ""
    d.text((40, 36), f"Speaking  ·  {task}" if task else "Speaking", font=F["header"], fill="white", anchor="lm")
    prefix = f"Part {part + 1}  ·  " if len(parts) > 1 and kind.startswith("lr") else ""
    right = (prefix + f"{idx + 1} of {n_lr}" if kind in ("lr_listen", "lr_answer", "lr_done")
             else f"Question {idx + 1} of {n_iv}" if kind in ("iv_listen", "iv_answer", "iv_done") else "")
    d.text((W - 40, 36), right, font=F["header_r"], fill="white", anchor="rm")
    d.rounded_rectangle((60, 100, W - 60, 660), radius=18, fill=CARD, outline=BORDER, width=2)

    if kind == "title":
        d.text((W / 2, 330), section["title"], font=F["title"], fill=INK, anchor="mm")
        n_sent = sum(len(x["sentences"]) for x in parts)
        what = (f"Listen and Repeat: {len(parts)} parts, {n_sent} sentences" if len(parts) > 1
                else f"Listen and Repeat ({n_sent} sentences)")
        if n_iv:
            what += f", then Take an Interview ({n_iv} questions)"
        d.text((W / 2, 400), what, font=F["body"], fill=MUTED, anchor="mm")
    elif kind == "end":
        d.text((W / 2, 340), "End of the Speaking section", font=F["title"], fill=INK, anchor="mm")
        d.text((W / 2, 410), "Stop your recording now.", font=F["body"], fill=MUTED, anchor="mm")
    else:
        if kind.startswith("lr"):
            labels = [s["spot"] for s in lr["sentences"]]
            current = -1 if kind == "lr_intro" else idx
            img.paste(campus(labels, current, lr.get("scene", "campus")), (90, 125))
            instruction = "Listen and repeat only once."
        else:
            av = avatar(kind in ("iv_intro", "iv_listen"))
            img.paste(av, (330 - av.width // 2, 360 - av.height // 2), av)
            d.text((330, 530), "Interviewer", font=F["body"], fill=MUTED, anchor="mm")
            instruction = "Please answer the interviewer's questions."
        d.line((680, 140, 680, 620), fill=BORDER, width=2)
        cx = 930
        d.text((cx, 160), instruction, font=F["body"], fill=MUTED, anchor="mm")
        status, color = {
            "lr_intro": ("Listen", INK), "lr_listen": ("Listen", INK), "lr_answer": ("Repeat now", GREEN),
            "lr_done": ("Time is up", RED), "iv_intro": ("Listen", INK), "iv_listen": ("Listen to the question", INK),
            "iv_answer": ("Answer now", GREEN), "iv_done": ("Time is up", RED),
        }[kind]
        if kind in ("lr_answer", "iv_answer"):
            tw = d.textlength(status, font=F["status"])
            d.ellipse((cx - tw / 2 - 34, 240 - 11, cx - tw / 2 - 12, 240 + 11), fill=GREEN)
            d.text((cx + 6, 240), status, font=F["status"], fill=color, anchor="mm")
        else:
            d.text((cx, 240), status, font=F["status"], fill=color, anchor="mm")
        if kind not in ("lr_intro", "iv_intro"):
            total = lr_seconds(idx) if kind.startswith("lr") else INTERVIEW_SECS
            if kind.endswith("listen"):
                shown, tcolor, frac = total, IDLE, 1.0
            elif kind.endswith("answer"):
                shown, frac = remaining, remaining / total
                tcolor = ORANGE if remaining <= (3 if kind.startswith("lr") else 10) else INK
            else:
                shown, tcolor, frac = 0, RED, 0.0
            d.text((cx, 320), "RESPONSE TIME", font=F["label"], fill=MUTED, anchor="mm")
            d.text((cx, 410), f"00:{shown:02d}", font=F["timer"], fill=tcolor, anchor="mm")
            bar = (cx - 210, 490, cx + 210, 506)
            d.rounded_rectangle(bar, radius=8, fill=TRACK)
            if frac > 0:
                fill = IDLE if kind.endswith("listen") else (ORANGE if tcolor == ORANGE else BLUE)
                d.rounded_rectangle((bar[0], bar[1], bar[0] + (bar[2] - bar[0]) * frac, bar[3]), radius=8, fill=fill)
    d.text((40, H - 30), "Practice simulation. Not an official ETS product.", font=F["small"], fill=IDLE, anchor="lm")
    img.save(path)
    return path


def window(kind, idx, secs):
    """Start beep plus a countdown of `secs` seconds, then the end beep: [(pcm, state), ...]."""
    out = [(np.concatenate([BEEP_START, silence(1.0)]), (kind + "_answer", idx, secs))]
    out += [(silence(1.0), (kind + "_answer", idx, r)) for r in range(secs - 1, 0, -1)]
    return out + [(BEEP_END, (kind + "_done", idx, 0))]


def main(section_path, out_dir):
    section = json.loads(Path(section_path).read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    parts, iv = lr_parts(section), section.get("interview")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        lines = {"outro": (section["narrator"], section["outro"])}
        recorded = {"outro": section.get("outro_audio")}
        for p_i, lr in enumerate(parts):
            lines[f"p{p_i}_lr_intro"] = (section["narrator"], lr["intro"])
            recorded[f"p{p_i}_lr_intro"] = lr.get("intro_audio")
            lines.update({f"p{p_i}_lr{i}": (lr["voice"], s["text"]) for i, s in enumerate(lr["sentences"])})
            # Prerecorded audio (e.g. official audio you own, or your own recordings) replaces TTS; paths are relative to the JSON file.
            recorded.update({f"p{p_i}_lr{i}": s.get("audio") for i, s in enumerate(lr["sentences"])})
        if iv:
            lines["iv_intro"] = (section["narrator"], iv["intro"])
            recorded["iv_intro"] = iv.get("intro_audio")
            lines.update({f"iv{i}": (iv["voice"], q) for i, q in enumerate(iv["questions"])})
            recorded.update({f"iv{i}": a for i, a in enumerate(iv.get("audio", []))})
        base = Path(section_path).resolve().parent
        for key, src in recorded.items():
            if src:
                ffmpeg("-i", str(base / src), "-vn", "-ac", "1", "-ar", str(RATE), "-sample_fmt", "s16", str(tmp / f"{key}.wav"))
        by_voice = {}
        for key, (voice, text) in lines.items():
            if not recorded.get(key):
                by_voice.setdefault(voice, []).append((tmp / f"{key}.wav", text))
        for voice, pairs in by_voice.items():
            print(f"synthesizing {len(pairs)} lines with {voice}")
            synthesize(voice, pairs)
        problems = 0
        for key, (voice, text) in lines.items():
            ratio, diffs = check(tmp / f"{key}.wav", text)
            if diffs:
                problems += 1
                print(f"CHECK {key} ({voice}, {ratio:.2f}): {'; '.join(diffs)}  | {text}")
        print(f"verified {len(lines)} lines, {problems} with differences")
        speech = {key: read_wav(tmp / f"{key}.wav") for key in lines}

        timeline = [(silence(2.5), ("title", 0, 0))]
        for p_i, lr in enumerate(parts):
            lead = silence(1.0) if p_i else silence(0)
            timeline.append((np.concatenate([lead, speech[f"p{p_i}_lr_intro"], silence(1.2)]), ("lr_intro", 0, 0, p_i)))
            for i, s in enumerate(lr["sentences"]):
                timeline.append((np.concatenate([speech[f"p{p_i}_lr{i}"], silence(LR_PAUSE)]), ("lr_listen", i, 0, p_i)))
                timeline += [(pcm, (*st, p_i)) for pcm, st in window("lr", i, lr_seconds(i))]
                timeline.append((silence(1.5), ("lr_done", i, 0, p_i)))
        if iv:
            timeline.append((np.concatenate([silence(1.0), speech["iv_intro"], silence(1.2)]), ("iv_intro", 0, 0)))
        for i in range(len(iv["questions"]) if iv else 0):
            timeline.append((np.concatenate([speech[f"iv{i}"], silence(0.6)]), ("iv_listen", i, 0)))
            timeline += window("iv", i, INTERVIEW_SECS)
            timeline.append((silence(2.0), ("iv_done", i, 0)))
        timeline.append((np.concatenate([speech["outro"], silence(1.5)]), ("end", 0, 0)))

        wav = tmp / "section.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(np.concatenate([pcm for pcm, _ in timeline]).tobytes())
        audio = out / f"{section['id']}.m4a"
        ffmpeg("-i", str(wav), "-c:a", "aac", "-b:a", "128k", str(audio))

        frames_dir = tmp / "frames"
        frames_dir.mkdir()
        listing = tmp / "frames.txt"
        with listing.open("w") as f:
            for pcm, state in timeline:
                last = frame(state, section, frames_dir)
                f.write(f"file '{last}'\nduration {len(pcm) / RATE:.4f}\n")
            f.write(f"file '{last}'\n")
        video = out / f"{section['id']}.mp4"
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-i", str(audio), "-vf", "fps=25,format=yuv420p",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "stillimage", "-c:a", "copy",
               "-shortest", "-movflags", "+faststart", str(video))
        total = sum(len(pcm) for pcm, _ in timeline) / RATE
        print(f"wrote {audio} and {video} ({total / 60:.1f} min)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
