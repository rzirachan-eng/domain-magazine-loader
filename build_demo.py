"""Build the fictional demo installation deterministically.

Every hash in the demo (sources, magazine, catalog, grants, installation) is
computed here, so the committed files can be regenerated and compared byte for
byte. The experiment, people and numbers below are invented.

    python build_demo.py            # rewrite ./demo
    python build_demo.py --out DIR  # write somewhere else
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

SOURCES = {
    "sources/experiment-report.md": [
        "# Checkout button experiment - report v1",
        "Date: 2026-03-02",
        "Variant B (green button) shows a +4.1% conversion uplift over control.",
        "The result is significant at p = 0.03 over 14 days.",
        "Traffic: 48,210 sessions in control, 48,090 in variant B.",
    ],
    "sources/correction.md": [
        "# Correction notice",
        "Date: 2026-03-09",
        "Bot traffic was found in the variant B arm (about 2,300 sessions).",
        "After removing it, the uplift is +1.9% and p = 0.21 (not significant).",
        "The +4.1% figure in report v1 must not be cited.",
    ],
    "sources/analyst-notes.md": [
        "# Reviewer notes",
        "Reviewer B disagrees with shipping on the corrected result.",
        "Concern: the test ran 14 days and covered only one pay cycle.",
        "Seasonality has not been controlled.",
    ],
    "sources/method.md": [
        "# Method: sample ratio check",
        "Run a chi-square test on the arm sizes before reading any metric.",
        "Flag the experiment for review if p < 0.01.",
    ],
    "sources/holdout.md": [
        "# Holdout slice (sealed)",
        "This slice must stay unread until the shipping decision is final.",
        "Q2 forecast: pending.",
    ],
    "sources/finance.md": [
        "# Finance memo",
        "Revenue impact estimate for the checkout change.",
    ],
}

ACTORS = ["analyst-a", "reviewer-b"]
AT = "2026-03-10T12:00:00+09:00"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def dump(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def source_ref(artifact, start, end):
    lines = SOURCES[artifact]
    blob = ("\n".join(lines) + "\n").encode("utf-8")
    excerpt = "\n".join(lines[start - 1:end])
    return {"artifact": artifact, "start_line": start, "end_line": end,
            "artifact_sha256": sha(blob), "excerpt_sha256": sha(excerpt.encode("utf-8"))}


def item(iid, kind, title, topics, known_at, basis, artifact, start, end, *,
         permission=None, embargo="CLEAR", supersedes=(), required=()):
    return {
        "id": iid, "kind": kind, "title": title, "topics": topics,
        "scope": "ab_test_review", "purposes": ["offline_audit"],
        "permission": permission if permission is not None else list(ACTORS),
        "known_at": known_at, "known_at_basis": basis, "embargo_oos": embargo,
        "supersedes": list(supersedes), "required_context": list(required),
        "source": source_ref(artifact, start, end),
    }


def magazine():
    return {
        "schema": "domain.magazine/1", "magazine_id": "ab-test-review",
        "version": "1.0.0", "domain": "ab_test_review",
        "title": "A/B test review (fictional demo)",
        "applicability": ["Offline review of a single fictional checkout experiment"],
        "limitations": ["All content is invented for demonstration",
                        "Hashes prove byte identity, not authorship or truth"],
        "items": [
            item("uplift-v1", "FACT", "Initial uplift reported in report v1",
                 ["conversion", "uplift"], "2026-03-02T09:00:00+09:00",
                 "Report date", "sources/experiment-report.md", 3, 4,
                 required=["seasonality-dissent"]),
            item("uplift-correction", "CORRECTION", "Uplift corrected after bot removal",
                 ["conversion", "uplift"], "2026-03-09T09:00:00+09:00",
                 "Correction notice date", "sources/correction.md", 3, 5,
                 supersedes=["uplift-v1"], required=["uplift-v1"]),
            item("seasonality-dissent", "DISSENT", "Reviewer objection: one pay cycle only",
                 ["seasonality"], "2026-03-09T10:00:00+09:00",
                 "Review note date", "sources/analyst-notes.md", 2, 4),
            item("srm-method", "METHOD", "Sample ratio check before reading metrics",
                 ["method", "sample-ratio"], "2026-03-01T09:00:00+09:00",
                 "Method note date", "sources/method.md", 2, 3),
            item("sealed-holdout", "FACT", "Sealed holdout slice",
                 ["holdout"], "2026-03-05T09:00:00+09:00",
                 "Slice creation date", "sources/holdout.md", 2, 2, embargo="EMBARGO"),
            item("q2-forecast", "HYPOTHESIS", "Q2 forecast (not yet available)",
                 ["forecast"], "2026-06-30T09:00:00+09:00",
                 "Planned publication date", "sources/holdout.md", 3, 3),
            item("finance-memo", "FACT", "Finance revenue estimate",
                 ["revenue"], "2026-03-04T09:00:00+09:00",
                 "Memo date", "sources/finance.md", 2, 2, permission=["reviewer-b"]),
        ],
    }


def build(out):
    out = Path(out)
    files = {}

    def put(rel, blob):
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        files[rel] = sha(blob)
        return {"path": rel, "sha256": sha(blob)}

    for rel, lines in SOURCES.items():
        put(rel, ("\n".join(lines) + "\n").encode("utf-8"))

    registry = put("bindings/registry.json", dump({"seats": [{"id": a} for a in ACTORS]}))
    identity = put("bindings/identity.json", dump({
        "revision": "ID-1",
        "seats": [{"immutable": {"agent_id": a}} for a in ACTORS]}))
    runtime = put("bindings/runtime.json", dump({"live_execution": False}))
    auth = put("config/authorization.json", dump({
        "schema": "domain.authorization/1",
        "human_instruction": "Approved: run the offline demo.",
        "recording_mode": "VERBATIM_USER_INSTRUCTION",
        "authorized_scope": ["offline_domain_context"],
        "not_authorized": ["live_execution"],
        "signature_status": "IMPLEMENTATION_AUTHORIZED_NOT_SIGNED"}))

    mref = put("library/ab-test-review.v1.json", dump(magazine()))
    catalog = put("config/catalog.json", dump({
        "schema": "domain.catalog/1", "version": "CAT-1",
        "magazines": [{"magazine_id": "ab-test-review", "version": "1.0.0",
                       "domain": "ab_test_review", "ref": mref}]}))
    grants = put("config/host-grants.json", dump({
        "schema": "domain.host-grants/1", "authorization": auth,
        "bindings": {"registry": registry, "identity": identity,
                     "runtime": runtime, "catalog": catalog},
        "grants": [{
            "work_order_id": "DEMO-AB-REVIEW", "actors": ["analyst-a"],
            "purpose": "offline_audit", "domains": ["ab_test_review"],
            "scopes": ["ab_test_review"], "source_paths": sorted(SOURCES),
            "not_before": "2026-03-10T00:00:00+09:00",
            "not_after": "2026-03-31T00:00:00+09:00",
            "byte_cap": 20000, "authority_type": "DIRECT_USER_OFFLINE",
            "task_db": None}]}))
    put("config/installation.json", dump({
        "schema": "domain.installation/1", "host_grants": grants, "catalog": catalog}))
    put("request.json", dump({
        "schema": "domain.request/1", "work_order_id": "DEMO-AB-REVIEW",
        "actor_id": "analyst-a", "purpose": "offline_audit",
        "domain": "ab_test_review", "topics": ["uplift", "conversion", "method"],
        "knowledge_cutoff": AT, "allowed_evidence_scopes": ["ab_test_review"],
        "identity_revision": "ID-1", "catalog_snapshot": catalog["sha256"],
        "byte_cap": 20000}))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=str(HERE / "demo"))
    args = parser.parse_args()
    files = build(args.out)
    print("wrote %d files to %s" % (len(files), args.out))


if __name__ == "__main__":
    main()
