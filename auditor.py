import json
import os
from datetime import datetime, timezone
from config import LOG_FILE
import config


def log_interaction(question: str, tier: str, response: str) -> None:
    """Append a structured record of this interaction to the audit log.

    Writes a single JSON object per line to `LOG_FILE` and prints a
    one-line terminal summary. Creates the logs directory if missing and
    gracefully handles write errors by falling back to console output.
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    q_trunc = question[:300]
    resp_preview = response[:200]

    entry = {
      "timestamp": timestamp,
      "tier": tier,
      "question": q_trunc,
      "response_preview": resp_preview,
      "response_length": len(response),
      "question_length": len(question),
      "model_version": getattr(config, "MODEL_VERSION", "unknown"),
    }

    # Ensure log directory exists (if any)
    dirpath = os.path.dirname(LOG_FILE)
    if dirpath:
      try:
        os.makedirs(dirpath, exist_ok=True)
      except OSError:
        print(f"[AUDIT ERROR] could not create log directory: {dirpath}")

    # Append JSON line to the logfile
    try:
      with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except (OSError, IOError) as e:
      print(f"[AUDIT ERROR] failed to write audit log: {e}")

    # One-line console summary
    single_line_preview = resp_preview.replace("\n", " ")
    print(f"[LOGGED] tier={tier} | \"{single_line_preview}\" → {len(response)} chars")
