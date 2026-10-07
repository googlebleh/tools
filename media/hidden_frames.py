#!/usr/bin/env python3
"""
hidden_frames.py - find single-frame "flash" inserts hidden inside a video.

Downloads a video with yt-dlp (or takes a local file), decodes every frame at a
tiny resolution, and looks for frames that are very different from BOTH their
neighbours while those neighbours are nearly identical to each other - i.e. the
video jumps away for a frame or three and then jumps right back. A normal scene
cut fails that test (the content after the cut does not match the content
before it), so real cuts get filtered out.

Examples
--------
    ./hidden_frames.py 'https://www.instagram.com/reel/XXXXXXXX/'
    ./hidden_frames.py clip.mp4 --max-run 5          # inserts up to 5 frames long
    ./hidden_frames.py URL --cookies-from-browser firefox
    ./hidden_frames.py clip.mp4 --min-jump 0.03 --ratio 2.0   # more sensitive
    ./hidden_frames.py clip.mp4 --dump-diffs                  # per-frame CSV

Output lands in ./<name>/ (change the parent with --outdir):
    frames/    full-resolution PNG of each suspected hidden frame
    context/   prev | hidden | next strip, to eyeball whether it is real
    report.json  (only with --report)
"""

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import numpy as np
from PIL import Image

# ----------------------------------------------------------------- utilities


def run(cmd, **kw):
    """Run a command, raise with its stderr if it fails."""
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise RuntimeError(
            "command failed (%d): %s\n%s" % (p.returncode, " ".join(cmd), p.stderr.strip())
        )
    return p.stdout


def need(tool):
    if shutil.which(tool) is None:
        sys.exit("error: %s not found on PATH" % tool)


def slugify(s, limit=60):
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    return (s or "video")[:limit]


def derive_name(url):
    """Pick a sane folder name from a URL: the last meaningful path segment."""
    path = urlsplit(url).path
    parts = [p for p in path.split("/") if p]
    generic = {"reel", "reels", "p", "video", "videos", "watch", "status", "v", "shorts"}
    for part in reversed(parts):
        if part.lower() not in generic:
            return slugify(part)
    q = parse_qs(urlsplit(url).query)
    for key in ("v", "id", "video_id"):
        if q.get(key):
            return slugify(q[key][0])
    return slugify(urlsplit(url).netloc or url)


# ----------------------------------------------------------------- download


def download(url, dest_dir, cookies_from_browser=None, cookies_file=None, extra=()):
    dest_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--no-progress",
        "--quiet",
        "--no-warnings",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
        "-o", str(dest_dir / "%(id)s.%(ext)s"),
        "--print", "after_move:filepath",
    ]
    if cookies_from_browser:
        cmd += ["--cookies-from-browser", cookies_from_browser]
    if cookies_file:
        cmd += ["--cookies", cookies_file]
    cmd += list(extra) + [url]

    try:
        out = run(cmd)
    except RuntimeError as e:
        msg = str(e)
        hint = ""
        if "login" in msg.lower() or "rate-limit" in msg.lower() or "cookies" in msg.lower():
            hint = (
                "\n\nInstagram often requires a logged-in session. Retry with e.g.\n"
                "    --cookies-from-browser firefox      (or chrome, chromium, brave)\n"
                "    --cookies cookies.txt"
            )
        sys.exit("yt-dlp failed.\n%s%s" % (msg, hint))

    for line in reversed(out.strip().splitlines()):
        p = Path(line.strip())
        if p.is_file():
            return p
    files = sorted(dest_dir.iterdir(), key=lambda p: p.stat().st_mtime)
    if files:
        return files[-1]
    sys.exit("yt-dlp reported success but no file was found in %s" % dest_dir)


# --------------------------------------------------------------------- probe


def probe(path):
    out = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,r_frame_rate,nb_frames",
        "-show_entries", "format=duration",
        "-of", "json", str(path),
    ])
    info = json.loads(out)
    if not info.get("streams"):
        sys.exit("no video stream in %s" % path)
    st = info["streams"][0]

    def rate(v):
        try:
            n, d = v.split("/")
            return float(n) / float(d) if float(d) else 0.0
        except Exception:
            return 0.0

    fps = rate(st.get("avg_frame_rate", "0/0")) or rate(st.get("r_frame_rate", "0/0")) or 30.0
    return {
        "width": int(st.get("width") or 0),
        "height": int(st.get("height") or 0),
        "fps": fps,
        "duration": float(info.get("format", {}).get("duration") or 0.0),
    }


# ------------------------------------------------------------------ analysis


def scan(path, size, max_run):
    """Decode every frame at size x size RGB and collect difference signals.

    Returns (n_frames, d, bridge) where
        d[j]          = mean |frame[j] - frame[j-1]|, normalised 0..1
        bridge[i, L]  = mean |frame[i+L] - frame[i-1]|  (content continuity
                        across a hypothetical hidden run of L frames at i)
    """
    bytes_per = size * size * 3
    proc = subprocess.Popen(
        [
            "ffmpeg", "-v", "error", "-nostdin", "-i", str(path),
            "-map", "0:v:0", "-an", "-sn", "-dn",
            "-vf", "scale=%d:%d:flags=bilinear" % (size, size),
            "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    ring_len = max_run + 2
    ring = [None] * ring_len
    d_list = []          # d_list[k] is the diff between frame k and k+1 -> d[k+1]
    bridges = {}         # (i, L) -> value
    j = 0
    buf = bytearray(bytes_per)
    view = memoryview(buf)

    def get(idx):
        return ring[idx % ring_len]

    while True:
        got = proc.stdout.readinto(view)
        if not got:
            break
        while got < bytes_per:
            more = proc.stdout.readinto(view[got:])
            if not more:
                break
            got += more
        if got < bytes_per:
            break

        cur = np.frombuffer(bytes(buf), dtype=np.uint8).astype(np.int16)
        ring[j % ring_len] = cur

        if j >= 1:
            d_list.append(float(np.abs(cur - get(j - 1)).mean()) / 255.0)
        for L in range(1, max_run + 1):
            i = j - L
            if i >= 1:
                bridges[(i, L)] = float(np.abs(cur - get(i - 1)).mean()) / 255.0
        j += 1

    proc.stdout.close()
    err = proc.stderr.read().decode("utf-8", "replace")
    proc.wait()
    if j == 0:
        sys.exit("ffmpeg decoded 0 frames.\n%s" % err.strip())

    d = np.zeros(j, dtype=np.float64)
    if d_list:
        d[1:] = np.asarray(d_list, dtype=np.float64)
    return j, d, bridges


def find_candidates(n, d, bridges, args):
    """Score every (start, run-length) pair and keep the ones that look hidden."""
    win = max(5, args.window)
    cands = []

    for (i, L), bridge in bridges.items():
        j = i + L
        if j >= n:
            continue
        d_in, d_out = d[i], d[j]
        flash = min(d_in, d_out)

        if flash < args.min_jump:
            continue
        if bridge > args.bridge_frac * flash:
            continue

        lo, hi = max(1, i - win), min(n, j + win + 1)
        local = np.concatenate([d[lo:i], d[j + 1:hi]])
        base = float(np.median(local)) if local.size else 0.0
        if flash < args.ratio * base:
            continue

        score = flash - bridge
        if score < args.min_score:
            continue
        cands.append({
            "start": i,
            "run": L,
            "d_in": d_in,
            "d_out": d_out,
            "bridge": bridge,
            "baseline": base,
            "score": score,
        })

    # Greedy de-duplication: overlapping (start, run) interpretations of the
    # same insert collapse to the single best-scoring one.
    cands.sort(key=lambda c: -c["score"])
    kept, taken = [], []
    for c in cands:
        a, b = c["start"] - 1, c["start"] + c["run"]
        if any(not (b < x or a > y) for x, y in taken):
            continue
        taken.append((a, b))
        kept.append(c)
    kept.sort(key=lambda c: c["start"])
    return kept


# ----------------------------------------------------------------- extraction


def extract(path, frame_numbers, dest):
    """Pull the given frame numbers out at full resolution. Returns {n: Path}."""
    frame_numbers = sorted(set(int(n) for n in frame_numbers if n >= 0))
    if not frame_numbers:
        return {}
    dest.mkdir(parents=True, exist_ok=True)
    expr = "+".join(r"eq(n\,%d)" % n for n in frame_numbers)
    with tempfile.TemporaryDirectory(dir=str(dest)) as td:
        base = [
            "ffmpeg", "-v", "error", "-nostdin", "-i", str(path),
            "-map", "0:v:0", "-vf", "select='%s'" % expr,
        ]
        tail = ["-f", "image2", str(Path(td) / "%06d.png")]
        # -vsync was dropped in ffmpeg 8, -fps_mode added in 5.1.
        try:
            run(base + ["-fps_mode", "passthrough"] + tail)
        except RuntimeError:
            run(base + ["-vsync", "0"] + tail)
        files = sorted(Path(td).glob("*.png"))
        if len(files) != len(frame_numbers):
            print(
                "warning: asked for %d frames, ffmpeg returned %d"
                % (len(frame_numbers), len(files)),
                file=sys.stderr,
            )
        out = {}
        for num, f in zip(frame_numbers, files):
            target = dest / ("f%06d.png" % num)
            shutil.move(str(f), str(target))
            out[num] = target
        return out


def strip(images, path, height=420, gap=8):
    """Write a horizontal prev|hidden|next contact strip."""
    ims = []
    for p in images:
        im = Image.open(p).convert("RGB")
        w = max(1, round(im.width * height / im.height))
        ims.append(im.resize((w, height), Image.LANCZOS))
    total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    sheet = Image.new("RGB", (total, height), (20, 20, 20))
    x = 0
    for im in ims:
        sheet.paste(im, (x, 0))
        x += im.width + gap
    sheet.save(path)


# ----------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(
        description="Find and extract single-frame hidden inserts in a video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples\n--------\n", 1)[-1],
    )
    ap.add_argument("source", help="video URL (anything yt-dlp handles) or a local file")
    ap.add_argument("-o", "--outdir", default=".",
                    help="where the per-video subfolder goes (default: current directory)")
    ap.add_argument("--name", help="subfolder name (default: derived from the video)")

    g = ap.add_argument_group("detection")
    g.add_argument("--max-run", type=int, default=4,
                   help="longest insert to look for, in frames (default: 4)")
    g.add_argument("--min-jump", type=float, default=0.05,
                   help="minimum normalised frame-to-frame change on both sides of the "
                        "insert, 0..1 (default: 0.05; lower = more sensitive)")
    g.add_argument("--bridge-frac", type=float, default=0.5,
                   help="how similar the frames on either side of the insert must be, "
                        "as a fraction of the jump (default: 0.5; lower = stricter)")
    g.add_argument("--ratio", type=float, default=3.0,
                   help="jump must be this many times the local median motion "
                        "(default: 3.0)")
    g.add_argument("--window", type=int, default=45,
                   help="frames each side used for the local motion baseline (default: 45)")
    g.add_argument("--min-score", type=float, default=0.0, help="drop candidates below this score")
    g.add_argument("--size", type=int, default=64,
                   help="analysis thumbnail size in px (default: 64)")
    g.add_argument("--top", type=int, default=25, help="extract at most N hits (default: 25)")

    g2 = ap.add_argument_group("download")
    g2.add_argument("--cookies-from-browser", metavar="BROWSER",
                    help="pass through to yt-dlp, e.g. firefox / chrome / brave")
    g2.add_argument("--cookies", metavar="FILE", help="cookies.txt for yt-dlp")
    g2.add_argument("--delete-video", action="store_true",
                    help="delete the downloaded video when done (default: keep it, so you "
                         "can re-run with different thresholds without downloading again)")
    g2.add_argument("--ytdlp-arg", action="append", default=[], metavar="ARG",
                    help="extra raw argument for yt-dlp (repeatable)")

    ap.add_argument("--report", action="store_true",
                    help="also write report.json with timestamps and detection metrics")
    ap.add_argument("--dump-diffs", action="store_true",
                    help="also write diffs.csv with the per-frame difference signal")
    ap.add_argument("--no-context", action="store_true", help="skip the prev|hit|next strips")
    args = ap.parse_args()

    need("ffmpeg")
    need("ffprobe")

    src = Path(args.source)
    is_local = src.exists()
    if not is_local:
        need("yt-dlp")

    name = args.name or (slugify(src.stem) if is_local else derive_name(args.source))
    workdir = Path(args.outdir) / name
    workdir.mkdir(parents=True, exist_ok=True)

    if is_local:
        video = src
    else:
        print("downloading %s" % args.source)
        video = download(args.source, workdir, args.cookies_from_browser,
                         args.cookies, args.ytdlp_arg)
    print("video: %s" % video)

    meta = probe(video)
    fps = meta["fps"]
    print("%dx%d  %.3f fps  %.2fs" % (meta["width"], meta["height"], fps, meta["duration"]))

    print("scanning frames...")
    n, d, bridges = scan(video, args.size, args.max_run)
    print("decoded %d frames" % n)

    if args.dump_diffs:
        with open(workdir / "diffs.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["frame", "time_s", "diff_from_prev"])
            for i in range(n):
                w.writerow([i, "%.4f" % (i / fps), "%.6f" % d[i]])
        print("wrote %s" % (workdir / "diffs.csv"))

    hits = find_candidates(n, d, bridges, args)
    if not hits:
        print("\nNo hidden frames found with the current settings.")
        print("Try a lower --min-jump (e.g. 0.03), a lower --ratio (e.g. 2.0),")
        print("or a larger --max-run. Use --dump-diffs to inspect the raw signal.")
        if args.report:
            (workdir / "report.json").write_text(json.dumps(
                {"video": str(video), "frames": n, "fps": fps, "hits": []}, indent=2))
        if args.delete_video and not is_local:
            video.unlink(missing_ok=True)
        return

    hits.sort(key=lambda c: -c["score"])
    hits = hits[: args.top]
    hits.sort(key=lambda c: c["start"])

    wanted = set()
    for c in hits:
        wanted.add(c["start"] - 1)
        for k in range(c["run"]):
            wanted.add(c["start"] + k)
        wanted.add(c["start"] + c["run"])
    frames = extract(video, wanted, workdir / "_raw")

    frames_dir = workdir / "frames"
    ctx_dir = workdir / "context"
    frames_dir.mkdir(exist_ok=True)
    if not args.no_context:
        ctx_dir.mkdir(exist_ok=True)

    print("\n%d hidden frame(s):\n" % len(hits))
    print("  #   frame     time      run   jump_in  jump_out  bridge   score")
    report = []
    for idx, c in enumerate(hits, 1):
        i, L = c["start"], c["run"]
        t = i / fps
        saved = []
        for k in range(L):
            srcf = frames.get(i + k)
            if not srcf:
                continue
            tag = "hidden_%02d_f%06d_t%07.3fs%s.png" % (
                idx, i + k, (i + k) / fps, ("_%d" % (k + 1)) if L > 1 else "")
            dst = frames_dir / tag
            shutil.copyfile(srcf, dst)
            saved.append(str(dst))

        ctx = None
        if not args.no_context:
            seq = [frames.get(i - 1)] + [frames.get(i + k) for k in range(L)] + [frames.get(i + L)]
            seq = [p for p in seq if p]
            if seq:
                ctx = ctx_dir / ("hidden_%02d_f%06d_context.png" % (idx, i))
                strip(seq, ctx)

        print("  %-3d %-9d %-9s %-5d %-8.3f %-9.3f %-8.3f %.3f" % (
            idx, i, "%.3fs" % t, L, c["d_in"], c["d_out"], c["bridge"], c["score"]))
        report.append({
            "index": idx, "frame": i, "time_s": round(t, 4),
            "duration_s": round(L / fps, 4), "run_frames": L,
            "jump_in": round(c["d_in"], 5), "jump_out": round(c["d_out"], 5),
            "bridge": round(c["bridge"], 5), "local_baseline": round(c["baseline"], 5),
            "score": round(c["score"], 5),
            "files": saved, "context": str(ctx) if ctx else None,
        })

    shutil.rmtree(workdir / "_raw", ignore_errors=True)
    if args.report:
        (workdir / "report.json").write_text(json.dumps({
            "video": str(video), "frames": n, "fps": fps,
            "duration_s": meta["duration"],
            "settings": {
                "max_run": args.max_run, "min_jump": args.min_jump,
                "bridge_frac": args.bridge_frac, "ratio": args.ratio,
                "window": args.window, "size": args.size,
            },
            "hits": report,
        }, indent=2))

    print("\nframes:  %s" % frames_dir)
    if not args.no_context:
        print("context: %s" % ctx_dir)
    if args.report:
        print("report:  %s" % (workdir / "report.json"))

    if args.delete_video and not is_local:
        video.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
