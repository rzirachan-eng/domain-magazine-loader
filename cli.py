"""Local entry point: render a task-bound magazine; no execution commands."""
import argparse
import json
import sys
from pathlib import Path
from domain_magazine import DEMO, Rejected, canonical, installed_loader

def main():
    parser = argparse.ArgumentParser(description="Offline domain magazine")
    parser.add_argument("--request", required=True)
    parser.add_argument("--root", default=str(DEMO),
                        help="trusted host directory holding config/")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    try:
        req = json.loads(Path(args.request).read_bytes())
        loader = installed_loader(args.root)
        pack = loader.load(req)
        result = {"pack": pack, "rendered": loader.render(pack)}
        if args.summary:
            result = {"outcome": pack["outcome"], "items": len(pack["items"]),
                      "pack_sha256": pack["pack_sha256"],
                      "excluded_items": pack["excluded_items"],
                      "serialized_bytes": len(canonical(pack)),
                      "usage": pack["usage"]}
        # ASCII output works in Windows GBK terminals without changing sources.
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except (Rejected, OSError, ValueError) as exc:
        print(json.dumps({"outcome": "REJECTED", "reason": str(exc)}, ensure_ascii=True))
        return 2

if __name__ == "__main__":
    sys.exit(main())
