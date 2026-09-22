#!/usr/bin/env python3
"""Create, query, validate and atomically patch entity manifests."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = Path(os.environ.get("LP_ASSETS_DIR", PROJECT_ROOT / ".assets")).resolve()
TEMPLATE_PATH = PROJECT_ROOT / "contracts" / "manifest.template.json"
SCHEMA_PATH = PROJECT_ROOT / "contracts" / "manifest.schema.json"
ENTITY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATUSES = {"pending", "running", "ready", "partial", "stale", "failed"}
LANDING_STATUSES = {"not_started", "running", "ready", "partial", "stale", "failed"}
PATH_KEYS = {"path", "data_path", "profile_path", "sources_path", "candidates_index", "briefing_path", "creative_direction_path"}
PATH_LIST_KEYS = {"output_paths"}

OWNERSHIP = {
    "instagram": {
        "instagram": None,
        "timestamps": {"instagram_collected_at"},
        "intake_status": {"instagram"},
        "cache": {"instagram"},
    },
    "web": {
        "web": None,
        "contact": None,
        "timestamps": {"web_collected_at"},
        "intake_status": {"web"},
        "cache": {"web"},
        "conflicts": None,
    },
    "landing_page": {"landing_page": None},
    "workflow": {"workflow": None, "intake_status": {"media"}},
}


class ManifestError(ValueError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_entity_id(entity_id: str) -> None:
    if len(entity_id) > 80 or not ENTITY_RE.fullmatch(entity_id):
        raise ManifestError("entity_id deve ser um slug minúsculo seguro")
    digits = re.sub(r"\D", "", entity_id)
    if len(digits) in {11, 14}:
        raise ManifestError("entity_id não pode incorporar CPF/CNPJ")


def entity_dir(entity_id: str) -> Path:
    validate_entity_id(entity_id)
    path = (ASSETS_ROOT / entity_id).resolve()
    if path.parent != ASSETS_ROOT:
        raise ManifestError("caminho de entidade fora de .assets")
    return path


def manifest_path(entity_id: str) -> Path:
    return entity_dir(entity_id) / "manifest.json"


def load_manifest(entity_id: str) -> dict[str, Any]:
    path = manifest_path(entity_id)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"manifest inexistente para {entity_id}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest JSON inválido: {exc.msg}") from exc


def safe_relative_path(value: str) -> bool:
    if not value or "\\" in value or value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return False
    return ".." not in PurePosixPath(value).parts


def parse_date(value: Any, label: str, errors: list[str], nullable: bool = True) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str):
        errors.append(f"{label} deve ser data ISO 8601")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} deve ser data ISO 8601")


def walk_paths(value: Any, errors: list[str], trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            current = trail + (key,)
            if key in PATH_KEYS and item is not None:
                if not isinstance(item, str) or not safe_relative_path(item):
                    errors.append(f"caminho inseguro em {'.'.join(current)}")
            elif key in PATH_LIST_KEYS:
                if not isinstance(item, list) or any(not isinstance(p, str) or not safe_relative_path(p) for p in item):
                    errors.append(f"lista de caminhos insegura em {'.'.join(current)}")
            walk_paths(item, errors, current)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk_paths(item, errors, trail + (str(index),))


def is_unmasked_document(value: Any) -> bool:
    if not isinstance(value, str) or "*" in value:
        return False
    return len(re.sub(r"\D", "", value)) in {11, 14}


def walk_sensitive(value: Any, errors: list[str], trail: tuple[str, ...] = (), sensitive: bool = False) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            marker = key.lower().replace("-", "_")
            child_sensitive = sensitive or marker in {"cpf", "cnpj", "document", "document_number", "document_value"}
            if child_sensitive and is_unmasked_document(item):
                errors.append(f"documento integral recusado em {'.'.join(trail + (key,))}")
            walk_sensitive(item, errors, trail + (key,), child_sensitive)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk_sensitive(item, errors, trail + (str(index),), sensitive)


def validate_manifest(data: Any, expected_entity_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest deve ser objeto JSON"]
    required = {
        "schema_version", "entity", "contact", "instagram", "web", "timestamps",
        "intake_status", "cache", "conflicts", "landing_page", "workflow", "created_at", "updated_at",
    }
    missing = sorted(required - data.keys())
    extra = sorted(data.keys() - required)
    if missing:
        errors.append(f"seções ausentes: {', '.join(missing)}")
    if extra:
        errors.append(f"seções desconhecidas: {', '.join(extra)}")
    if data.get("schema_version") != "1.0":
        errors.append("schema_version deve ser 1.0")

    # Apply the published contract when jsonschema is available, while keeping
    # the CLI usable with the Python standard library alone.
    try:
        from jsonschema import Draft202012Validator

        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        for issue in Draft202012Validator(schema).iter_errors(data):
            location = ".".join(str(item) for item in issue.absolute_path) or "manifest"
            message = f"schema {location}: viola {issue.validator}"
            if message not in errors:
                errors.append(message)
    except ImportError:
        pass

    entity = data.get("entity")
    if not isinstance(entity, dict):
        errors.append("entity deve ser objeto")
    else:
        try:
            validate_entity_id(entity.get("id", ""))
        except ManifestError as exc:
            errors.append(str(exc))
        if expected_entity_id and entity.get("id") != expected_entity_id:
            errors.append("entity.id diverge do diretório")
        if not isinstance(entity.get("display_name"), str) or not entity.get("display_name", "").strip():
            errors.append("entity.display_name é obrigatório")
        document = entity.get("document")
        if not isinstance(document, dict) or set(document) != {"type", "value"}:
            errors.append("entity.document deve conter type e value")
        else:
            doc_value = document.get("value")
            if doc_value is not None:
                digits = re.sub(r"\D", "", doc_value) if isinstance(doc_value, str) else ""
                if not isinstance(doc_value, str) or "*" not in doc_value or len(digits) > 6 or not re.fullmatch(r"[0-9*./-]+", doc_value):
                    errors.append("entity.document.value deve ser null ou mascarado")

    statuses = data.get("intake_status")
    if not isinstance(statuses, dict) or set(statuses) != {"instagram", "web", "media"}:
        errors.append("intake_status deve conter instagram, web e media")
    elif any(value not in STATUSES for value in statuses.values()):
        errors.append("intake_status contém estado inválido")

    landing = data.get("landing_page")
    if not isinstance(landing, dict) or landing.get("status") not in LANDING_STATUSES:
        errors.append("landing_page.status inválido")
    workflow = data.get("workflow")
    if not isinstance(workflow, dict) or workflow.get("status") not in STATUSES:
        errors.append("workflow.status inválido")

    cache = data.get("cache")
    if not isinstance(cache, dict) or set(cache) != {"instagram", "web"}:
        errors.append("cache deve conter instagram e web")
    else:
        for domain in ("instagram", "web"):
            entry = cache.get(domain)
            if not isinstance(entry, dict) or set(entry) != {"fingerprint", "collected_at", "expires_at"}:
                errors.append(f"cache.{domain} inválido")
                continue
            parse_date(entry.get("collected_at"), f"cache.{domain}.collected_at", errors)
            parse_date(entry.get("expires_at"), f"cache.{domain}.expires_at", errors)

    conflicts = data.get("conflicts")
    if not isinstance(conflicts, list):
        errors.append("conflicts deve ser lista")
    else:
        for index, conflict in enumerate(conflicts):
            if not isinstance(conflict, dict) or not conflict.get("field") or conflict.get("status") not in {"open", "resolved"}:
                errors.append(f"conflicts.{index} inválido")
                continue
            values = conflict.get("values")
            if not isinstance(values, list) or len(values) < 2:
                errors.append(f"conflicts.{index}.values exige ao menos dois valores")
            else:
                for value_index, item in enumerate(values):
                    if not isinstance(item, dict) or not all(key in item for key in ("value", "source", "url", "observed_at")):
                        errors.append(f"conflicts.{index}.values.{value_index} inválido")
                    elif any(marker in str(conflict.get("field", "")).lower() for marker in ("cpf", "cnpj", "document")) and is_unmasked_document(item.get("value")):
                        errors.append(f"documento integral recusado em conflicts.{index}.values.{value_index}")

    parse_date(data.get("created_at"), "created_at", errors, nullable=False)
    parse_date(data.get("updated_at"), "updated_at", errors, nullable=False)
    for section in ("contact", "instagram", "web", "timestamps"):
        if not isinstance(data.get(section), dict):
            errors.append(f"{section} deve ser objeto")
    walk_paths(data, errors)
    walk_sensitive(data, errors)
    return errors


def deep_merge(base: Any, patch: Any) -> Any:
    if isinstance(base, dict) and isinstance(patch, dict):
        result = copy.deepcopy(base)
        for key, value in patch.items():
            result[key] = deep_merge(result.get(key), value)
        return result
    return copy.deepcopy(patch)


def validate_ownership(owner: str, patch: Any) -> None:
    if not isinstance(patch, dict) or not patch:
        raise ManifestError("patch deve ser objeto JSON não vazio")
    allowed = OWNERSHIP[owner]
    for top_key, value in patch.items():
        if top_key not in allowed:
            raise ManifestError(f"owner {owner} não pode escrever {top_key}")
        children = allowed[top_key]
        if children is not None:
            if not isinstance(value, dict) or not set(value).issubset(children):
                raise ManifestError(f"owner {owner} excedeu ownership de {top_key}")


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=".manifest-", suffix=".tmp", delete=False)
    temp_path = Path(handle.name)
    try:
        with handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def log_event(entity_id: str, event: str, detail: str | None = None) -> None:
    directory = entity_dir(entity_id) / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    record = {"at": now_iso(), "event": event}
    if detail:
        record["detail"] = detail[:500]
    with (directory / "manifest.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    path = manifest_path(args.entity_id)
    if path.exists():
        raise ManifestError("manifest já existe")
    stamp = now_iso()
    data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    data["entity"]["id"] = args.entity_id
    data["entity"]["display_name"] = args.display_name
    data["created_at"] = stamp
    data["updated_at"] = stamp
    errors = validate_manifest(data, args.entity_id)
    if errors:
        raise ManifestError("; ".join(errors))
    atomic_write(path, data)
    for child in ("instagram/profile", "instagram/posts", "instagram/candidates", "web/raws", "logs"):
        (path.parent / child).mkdir(parents=True, exist_ok=True)
    log_event(args.entity_id, "initialized")
    return {"ok": True, "entity_id": args.entity_id, "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/") if path.is_relative_to(PROJECT_ROOT) else str(path)}


def command_get(args: argparse.Namespace) -> Any:
    value: Any = load_manifest(args.entity_id)
    if args.section:
        for part in args.section.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                value = value[int(part)]
            else:
                raise ManifestError(f"caminho inexistente: {args.section}")
    return {"ok": True, "value": value}


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    data = load_manifest(args.entity_id)
    return {
        "ok": True,
        "entity_id": args.entity_id,
        "intake_status": data["intake_status"],
        "landing_page": data["landing_page"]["status"],
        "workflow": data["workflow"],
        "cache": data["cache"],
        "open_conflicts": sum(item.get("status") == "open" for item in data["conflicts"]),
    }


def command_patch(args: argparse.Namespace) -> dict[str, Any]:
    path = manifest_path(args.entity_id)
    original = load_manifest(args.entity_id)
    try:
        patch = json.loads(Path(args.patch_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"patch inválido: {exc}") from exc
    validate_ownership(args.owner, patch)
    candidate = deep_merge(original, patch)
    candidate["updated_at"] = now_iso()
    errors = validate_manifest(candidate, args.entity_id)
    if errors:
        log_event(args.entity_id, "patch_rejected", "; ".join(errors))
        raise ManifestError("; ".join(errors))
    atomic_write(path, candidate)
    log_event(args.entity_id, "patched", args.owner)
    return {"ok": True, "entity_id": args.entity_id, "owner": args.owner, "updated_at": candidate["updated_at"]}


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    errors = validate_manifest(load_manifest(args.entity_id), args.entity_id)
    if errors:
        log_event(args.entity_id, "validation_failed", "; ".join(errors))
        raise ManifestError("; ".join(errors))
    return {"ok": True, "entity_id": args.entity_id, "schema_version": "1.0"}


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("entity_id")
    init.add_argument("--display-name", required=True)
    init.set_defaults(handler=command_init)
    get = commands.add_parser("get")
    get.add_argument("entity_id")
    get.add_argument("section", nargs="?")
    get.set_defaults(handler=command_get)
    status = commands.add_parser("status")
    status.add_argument("entity_id")
    status.set_defaults(handler=command_status)
    patch = commands.add_parser("patch")
    patch.add_argument("entity_id")
    patch.add_argument("owner", choices=sorted(OWNERSHIP))
    patch.add_argument("patch_file")
    patch.set_defaults(handler=command_patch)
    validate = commands.add_parser("validate")
    validate.add_argument("entity_id")
    validate.set_defaults(handler=command_validate)
    return cli


def main() -> int:
    args = parser().parse_args()
    try:
        result = args.handler(args)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except ManifestError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
