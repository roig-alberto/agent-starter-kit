#!/usr/bin/env python3
"""Fetch a YouTube video's transcript politely, one request at a time.

Usage: python3 ~/.claude/scripts/yt-transcript.py <out-dir> <url|id> [<url|id> ...]
Writes <out-dir>/<id>.info.json (yt-dlp metadata), <id>.txt (plain transcript) and <id>.timed.txt (the same text as
"[m:ss] text" lines, one per 20 seconds, for minute-exact notes). Tries the caption file once; when
it is missing or rate-limited (HTTP 429), downloads the audio and transcribes it locally with faster-whisper (CPU,
model "small", run through uv so nothing is installed). A yt-dlp call that gets HTTP 429 (metadata or audio) waits 1,
2, 4, 8 then 15 minutes plus up to 30 s of jitter before each retry; a video still limited after that skips the rest
of the batch. Never switches client to dodge a limit: a 429 means wait. Exits 1 when any video got no transcript.
Every yt-dlp call also takes a turn in the research repo's shared YouTube slot file (tools/pace.ts), so this script and
youtube.ts running at the same time stay 3 s apart.
An Instagram reel or post link (instagram.com/reel/<code>/) has no caption file: it goes straight to the audio and
whisper path, without the YouTube slot, and its files are named by the shortcode (<code>.info.json, .txt, .timed.txt).
"""
import glob, json, os, random, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

WAITS = [60, 120, 240, 480, 900]
LANGS = ["en-orig", "es-orig", "en", "es"]  # when the video's own language has no track; "-orig" is not a translation
ID = re.compile(r"[A-Za-z0-9_-]{11}")
REEL = re.compile(r"[A-Za-z0-9_-]{5,}")
# The research repo's pace folder (tools/pace.ts): the same lock and slot file, the same 3 s gap for YouTube.
PACE_DIR = os.environ.get("RESEARCH_PACE_DIR") or os.path.join(
    os.path.dirname(os.environ.get("RESEARCH_LOG") or os.path.expanduser("~/.local/share/research/fetches.jsonl")), "pace")
YT_GAP_MS = 3000
STALE_LOCK_S = 10
# faster-whisper calls av.open(metadata_errors=...), which PyAV 16 dropped (2026-10-28); 15.1.0 ships wheels.
WHISPER = ["uv", "run", "-q", "--no-project", "--python", "3.12", "--with", "faster-whisper", "--with", "av==15.1.0",
           "python", "-I", "-c",
           "import sys; from faster_whisper import WhisperModel; "
           "segs, _ = WhisperModel('small', device='cpu', compute_type='int8').transcribe(sys.argv[1], beam_size=5); "
           "print('\\n'.join(f'{s.start:.1f}\\t{s.text.strip()}' for s in segs))"]


class RateLimited(Exception):
    pass


def video_id(arg):
    """The 11-character ID from a bare ID or any watch, youtu.be, shorts, live or embed link (share junk dropped)."""
    if ID.fullmatch(arg):
        return arg
    u = urllib.parse.urlparse(arg if "//" in arg else "https://" + arg)
    parts = [p for p in u.path.split("/") if p]
    if u.hostname and u.hostname.endswith("youtu.be") and parts:
        cand = parts[0]
    elif len(parts) >= 2 and parts[0] in ("shorts", "live", "embed", "v"):
        cand = parts[1]
    else:
        cand = urllib.parse.parse_qs(u.query).get("v", [""])[0]
    if not ID.fullmatch(cand):
        raise ValueError(f"no YouTube video ID in {arg!r}")
    return cand


def reel_id(arg):
    """The shortcode of an Instagram reel or post link, or None for anything else."""
    u = urllib.parse.urlparse(arg if "//" in arg else "https://" + arg)
    parts = [p for p in u.path.split("/") if p]
    if (u.hostname or "").endswith("instagram.com") and len(parts) >= 2 and parts[0] in ("reel", "reels", "p") \
            and REEL.fullmatch(parts[1]):
        return parts[1]
    return None


def pace():
    """Wait for the next free YouTube slot, shared with tools/pace.ts. A file error means no wait, never a failure."""
    lock, slots = os.path.join(PACE_DIR, "youtube.com.lock"), os.path.join(PACE_DIR, "youtube.com.next")
    try:
        os.makedirs(PACE_DIR, exist_ok=True)
        while True:
            try:
                os.mkdir(lock)
                break
            except FileExistsError:
                try:
                    if time.time() - os.stat(lock).st_mtime > STALE_LOCK_S:
                        os.rmdir(lock)
                except OSError:
                    pass
                time.sleep(0.01 + random.random() * 0.03)
        try:
            try:
                nxt = float(open(slots).read() or 0)
            except (OSError, ValueError):
                nxt = 0
            now = time.time() * 1000
            slot = max(now, nxt)
            open(slots, "w").write(str(int(slot + YT_GAP_MS)))
        finally:
            os.rmdir(lock)
    except OSError as e:
        print(f"pacing skipped: {e}", flush=True)
        return
    if slot > now:
        time.sleep((slot - now) / 1000)


def yt_dlp(vid, what, args, paced=True):
    """Run yt-dlp; on HTTP 429 wait and retry, raise RateLimited when the waits are used up."""
    for attempt, wait in enumerate([0] + WAITS):
        if wait:
            time.sleep(wait + random.uniform(0, 30))
        if paced:
            pace()
        r = subprocess.run(["yt-dlp"] + args, capture_output=True, text=True, timeout=1800)
        if "HTTP Error 429" not in r.stderr:
            return r
        print(f"{vid}: {what} got HTTP 429 on attempt {attempt + 1}", flush=True)
    raise RateLimited(f"{vid}: {what} still rate-limited after {len(WAITS) + 1} attempts")


def last_error(r):
    return (r.stderr.strip().splitlines() or ["no error text"])[-1][:200]


def caption_url(info):
    """Manual subtitles first, then auto captions; the video's own language (YouTube says "en-US", tracks say "en")
    before the fallbacks, and the original auto track ("es-orig") before a machine translation ("es", "en")."""
    lang = info.get("language") or ""
    base = lang.split("-")[0]
    order = {"subtitles": [lang, base], "automatic_captions": [f"{base}-orig", lang, base] if base else []}
    for kind, first in order.items():
        for key in [k for k in first if k] + LANGS:
            for t in (info.get(kind) or {}).get(key, []):
                if t.get("ext") == "json3":
                    return kind, key, t["url"]
    return None


def expired(cap, margin_s=600):
    """Caption links are signed and expire (about 7 hours after the metadata, measured 2026-10-28)."""
    exp = urllib.parse.parse_qs(urllib.parse.urlparse(cap).query).get("expire", [""])[0]
    return exp.isdigit() and int(exp) < time.time() + margin_s


def text_of(raw):
    events = json.loads(raw).get("events", [])
    return " ".join(" ".join(s.get("utf8", "") for e in events for s in e.get("segs", [])).split())


def stamp(sec):
    return f"[{int(sec) // 60}:{int(sec) % 60:02d}]"


def timed(pairs, every=20):
    """(start seconds, text) pairs to lines "[m:ss] text", one line per `every` seconds, for minute-exact notes."""
    lines, cur, start = [], [], None
    for t, text in pairs:
        if start is None:
            start = t
        if t - start >= every and cur:
            lines.append(f"{stamp(start)} {' '.join(' '.join(cur).split())}")
            cur, start = [], t
        cur.append(text)
    if cur:
        lines.append(f"{stamp(start)} {' '.join(' '.join(cur).split())}")
    return "\n".join(lines) + "\n"


def timed_of(raw):
    events = json.loads(raw).get("events", [])
    return timed([(e.get("tStartMs", 0) / 1000, "".join(s.get("utf8", "") for s in e.get("segs", []))) for e in events if e.get("segs")])


def metadata(out, vid, url):
    info_path = f"{out}/{vid}.info.json"
    if os.path.exists(info_path):
        info = json.load(open(info_path, encoding="utf-8"))
        found = caption_url(info)
        if not (found and expired(found[2])):
            return info
        os.remove(info_path)  # saved metadata from an earlier run: its caption links no longer work
    r = yt_dlp(vid, "metadata", ["--skip-download", "--write-info-json", "-o", f"{out}/{vid}.%(ext)s", url])
    if not os.path.exists(info_path):
        raise RuntimeError(f"{vid}: no metadata (yt-dlp: {last_error(r)})")
    return json.load(open(info_path, encoding="utf-8"))


def from_audio(out, vid, url, fmt="bestaudio", extra=(), paced=True):
    r = yt_dlp(vid, "audio download", ["-q", "--no-warnings", "-f", fmt, "-o", f"{out}/{vid}.audio.%(ext)s", *extra, url],
               paced)
    audio = glob.glob(f"{out}/{vid}.audio.*")
    if not audio:
        raise RuntimeError(f"{vid}: audio download failed (yt-dlp: {last_error(r)})")
    w = subprocess.run(WHISPER + [audio[0]], capture_output=True, text=True)
    if w.returncode != 0 or not w.stdout.strip():
        raise RuntimeError(f"{vid}: whisper failed: {w.stderr.strip().splitlines()[-1:]}")
    pairs = [(float(a), b) for a, _, b in (l.partition("\t") for l in w.stdout.strip().splitlines()) if b]
    open(f"{out}/{vid}.txt", "w", encoding="utf-8").write(" ".join(b.strip() for _, b in pairs) + "\n")
    open(f"{out}/{vid}.timed.txt", "w", encoding="utf-8").write(timed(pairs))
    os.remove(audio[0])
    return f"{vid}: ok (audio and whisper)"


def fetch(out, vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    found = caption_url(metadata(out, vid, url))
    if found:
        kind, lang, cap = found
        try:
            raw = urllib.request.urlopen(cap, timeout=30).read().decode("utf-8")
            open(f"{out}/{vid}.txt", "w", encoding="utf-8").write(text_of(raw) + "\n")
            open(f"{out}/{vid}.timed.txt", "w", encoding="utf-8").write(timed_of(raw))
            return f"{vid}: ok ({kind} {lang})"
        except (OSError, ValueError) as e:  # HTTP errors, timeouts, dropped connections, a broken caption file
            print(f"{vid}: captions failed ({getattr(e, 'code', None) or e}), using the audio", flush=True)
    return from_audio(out, vid, url)


def fetch_reel(out, code, url):
    # An Instagram reel can be a muxed video with no audio-only format; the info.json comes from the same call.
    return from_audio(out, code, url, "bestaudio/best", ["--write-info-json", "-o", f"infojson:{out}/{code}"], False)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: yt-transcript.py <out-dir> <url|id> [<url|id> ...]")
    out, args = sys.argv[1], sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    failed = 0
    for i, arg in enumerate(args):
        if i:
            time.sleep(random.uniform(5, 15))
        try:
            code = reel_id(arg)
            print(fetch_reel(out, code, arg) if code else fetch(out, video_id(arg)), flush=True)
        except RateLimited as e:
            rest = args[i + 1:]
            print(f"{e}; not tried: {' '.join(rest)}" if rest else str(e), flush=True)
            failed += 1 + len(rest)
            break
        except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as e:
            print(f"{arg}: {e}", flush=True)  # this video failed; the batch goes on
            failed += 1
    sys.exit(1 if failed else 0)
