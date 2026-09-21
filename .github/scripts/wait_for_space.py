#!/usr/bin/env python3
"""Block until a pushed Space commit reaches a terminal runtime stage."""

import argparse
import os
import sys
import time

from huggingface_hub import HfApi

BUSY = {"BUILDING", "RUNNING_BUILDING", "APP_STARTING"}
GOOD = {"RUNNING", "SLEEPING"}
BAD = {"BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR", "NO_APP_FILE", "PAUSED"}

parser = argparse.ArgumentParser()
parser.add_argument("--space", required=True)
parser.add_argument("--sha", required=True)
parser.add_argument("--timeout-minutes", type=int, default=40)
args = parser.parse_args()

api = HfApi(token=os.environ["HF_TOKEN"])
started = time.monotonic()
deadline = started + args.timeout_minutes * 60
last = None

# The previous build still reports RUNNING for a few seconds after a push, so a
# stage must be observed leaving BUILDING before RUNNING counts as this deploy.
saw_busy = False

# A never-built Space reports NO_APP_FILE, and HF takes a moment to notice the
# push. Failing stages are only terminal once the build has started, or once
# this window closes without one.
GRACE_SECONDS = 180

while time.monotonic() < deadline:
    stage = api.get_space_runtime(args.space).stage
    if stage != last:
        print(f"[{int(time.monotonic() - started)}s] stage={stage}", flush=True)
        last = stage
    if stage in BUSY:
        saw_busy = True
    elif stage in BAD:
        if saw_busy or time.monotonic() - started > GRACE_SECONDS:
            sys.exit(f"Space {args.space} failed to deploy {args.sha[:8]}: {stage}")
    elif stage in GOOD and saw_busy:
        print(f"Space {args.space} is {stage} on {args.sha[:8]}.")
        sys.exit(0)
    time.sleep(10)

sys.exit(f"Timed out after {args.timeout_minutes}m; last stage was {last}.")
