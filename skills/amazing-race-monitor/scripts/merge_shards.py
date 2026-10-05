#!/usr/bin/env python3
"""Merge shard review files into data/amazing-race/flags.json.

Single-writer merge for the sharded vision review. Reads every
data/amazing-race/flags-shard-*.json (JSON arrays of flag objects), merges them
into flags.json, dedupes by post_id (keeps the flag already in flags.json
first, then the first shard flag per post), guarantees unique flag_ids, and
deletes the consumed shard files. Print a one-line summary.

Usage: merge_shards.py [--dry-run]
"""

import glob
import json
import os
import sys
import time

IES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_DIR = os.path.join(IES_ROOT, "data", "amazing-race")
FLAGS_PATH = os.path.join(DATA_DIR, "flags.json")


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def main():
    dry = "--dry-run" in sys.argv
    flags = load(FLAGS_PATH, [])
    by_post = {f.get("post_id"): f for f in flags if f.get("post_id")}
    taken_ids = {f.get("flag_id") for f in flags}
    shards = sorted(glob.glob(os.path.join(DATA_DIR, "flags-shard-*.json")))
    added, dupes = 0, 0
    for sp in shards:
        for f in load(sp, []):
            pid = f.get("post_id")
            if pid and pid in by_post:
                dupes += 1
                continue  # already flagged — keep the first
            if pid:
                by_post[pid] = f
            # unique flag_id
            fid = f.get("flag_id") or "UNK-%d" % (len(flags) + added + 1)
            base = fid
            n = 2
            while fid in taken_ids:
                fid = "%s-%d" % (base, n)
                n += 1
            f["flag_id"] = fid
            taken_ids.add(fid)
            flags.append(f)
            added += 1
    print(json.dumps({"ok": True, "merged_shards": len(shards), "flags_added": added,
                      "duplicates_skipped": dupes, "total_flags": len(flags),
                      "merged_at": time.strftime("%Y-%m-%dT%H:%M:%S")}))
    if dry:
        return
    tmp = FLAGS_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(flags, f, indent=2)
    os.replace(tmp, FLAGS_PATH)
    for sp in shards:
        os.remove(sp)


if __name__ == "__main__":
    main()
