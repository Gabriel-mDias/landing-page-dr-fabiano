#!/usr/bin/env python3
"""Produce the deterministic execution plan for the landing-page workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Any

import manifest


TTLS = {"instagram": timedelta(hours=24), "web": timedelta(days=7)}


def slugify(display_name: str) -> str:
    normalized = unicodedata.normalize("NFKD", display_name).encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")[:80].strip("-")
    digits = re.sub(r"\D", "", display_name)
    if not slug or len(digits) in {11, 14} and digits in slug.replace("-", ""):
        raise manifest.ManifestError("nome não produz entity_id seguro sem CPF/CNPJ")
    manifest.validate_entity_id(slug)
    return slug


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def cache_state(data: dict[str, Any], domain: str, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    entry = data["cache"][domain]
    expiry = parse_timestamp(entry.get("expires_at"))
    if expiry is None:
        collected = parse_timestamp(entry.get("collected_at"))
        expiry = collected + TTLS[domain] if collected else None
    status = data["intake_status"][domain]
    if status != "ready" or not entry.get("fingerprint"):
        return "missing" if status == "pending" else status
    return "valid" if expiry and expiry > now else "stale"


def build_plan(
    data: dict[str, Any], *, refresh: bool = False, refresh_instagram: bool = False,
    refresh_web: bool = False, existing_only: bool = False, now: datetime | None = None,
) -> dict[str, Any]:
    states = {domain: cache_state(data, domain, now) for domain in ("instagram", "web")}
    requested = {
        "instagram": refresh or refresh_instagram,
        "web": refresh or refresh_web,
    }
    actions: list[str] = []
    gaps: list[str] = []
    blockers: list[str] = []
    for domain in ("instagram", "web"):
        needs_intake = requested[domain] or states[domain] != "valid"
        if needs_intake:
            reason = "refresh_requested" if requested[domain] else states[domain]
            blockers.append(f"intake_{domain}_{reason}")
            if existing_only:
                gaps.append(f"{domain}:{'refresh-requested' if requested[domain] else states[domain]}")
            else:
                actions.append(f"collect_{domain}")

    open_conflicts = sum(item.get("status") == "open" for item in data.get("conflicts", []))
    if open_conflicts:
        blockers.append("open_conflicts")
    media_status = data.get("intake_status", {}).get("media")
    if media_status != "ready":
        blockers.append(f"media_{media_status or 'missing'}")

    has_collection = any(action.startswith("collect_") for action in actions)
    requires_replan = has_collection
    builder_ready = not blockers
    if has_collection:
        stage = "intake"
        actions.append("replan")
    elif builder_ready:
        stage = "builder"
        actions.extend(["validate_manifest", "run_builder"])
    else:
        stage = "blocked"
        actions.append("stop_existing_data_insufficient" if existing_only else "resolve_blockers")
    return {
        "cache": states,
        "refresh": requested,
        "existing_only": existing_only,
        "actions": actions,
        "gaps": gaps,
        "open_conflicts": open_conflicts,
        "stage": stage,
        "blockers": blockers,
        "requires_replan": requires_replan,
        "builder_ready": builder_ready,
    }


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("entity_id")
    plan.add_argument("--refresh", action="store_true")
    plan.add_argument("--refresh-instagram", action="store_true")
    plan.add_argument("--refresh-web", action="store_true")
    plan.add_argument("--existing-only", action="store_true")
    slug = commands.add_parser("slug")
    slug.add_argument("display_name")
    args = cli.parse_args()
    try:
        if args.command == "slug":
            result = {"ok": True, "entity_id": slugify(args.display_name)}
        else:
            data = manifest.load_manifest(args.entity_id)
            errors = manifest.validate_manifest(data, args.entity_id)
            if errors:
                raise manifest.ManifestError("; ".join(errors))
            result = {"ok": True, "entity_id": args.entity_id, **build_plan(
                data,
                refresh=args.refresh,
                refresh_instagram=args.refresh_instagram,
                refresh_web=args.refresh_web,
                existing_only=args.existing_only,
            )}
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except manifest.ManifestError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
