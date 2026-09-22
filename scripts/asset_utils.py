#!/usr/bin/env python3
"""Deterministic media inventory, download and heuristic classification."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import mimetypes
import os
import re
import socket
import struct
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
ROLE_WORDS = {
    "logo": ("logo", "marca", "brand", "avatar", "perfil", "profile"),
    "hero": ("hero", "banner", "capa", "cover", "header"),
    "portrait": ("retrato", "portrait", "headshot", "equipe", "team", "founder"),
    "gallery": ("gallery", "galeria", "produto", "product", "portfolio", "projeto"),
}


class AssetError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_info(data: bytes) -> tuple[int, int, bool]:
    if len(data) < 26 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssetError("PNG inválido")
    width, height = struct.unpack(">II", data[16:24])
    color_type = data[25]
    return width, height, color_type in {4, 6} or b"tRNS" in data


def gif_info(data: bytes) -> tuple[int, int, bool]:
    if len(data) < 10 or data[:6] not in {b"GIF87a", b"GIF89a"}:
        raise AssetError("GIF inválido")
    width, height = struct.unpack("<HH", data[6:10])
    return width, height, b"\x21\xf9\x04" in data


def jpeg_info(data: bytes) -> tuple[int, int, bool]:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise AssetError("JPEG inválido")
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            break
        length = struct.unpack(">H", data[index:index + 2])[0]
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF} and index + 7 <= len(data):
            height, width = struct.unpack(">HH", data[index + 3:index + 7])
            return width, height, False
        index += max(length, 2)
    raise AssetError("dimensões JPEG ausentes")


def webp_info(data: bytes) -> tuple[int, int, bool]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise AssetError("WebP inválido")
    kind = data[12:16]
    if kind == b"VP8X":
        flags = data[20]
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height, bool(flags & 0x10)
    if kind == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF, False
    if kind == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1, True
    raise AssetError("variante WebP não reconhecida")


def svg_info(data: bytes) -> tuple[int | None, int | None, bool]:
    text = data.decode("utf-8", errors="ignore")[:65536]
    if "<svg" not in text:
        raise AssetError("SVG inválido")
    width_match = re.search(r"\bwidth=[\"']([0-9.]+)", text)
    height_match = re.search(r"\bheight=[\"']([0-9.]+)", text)
    if width_match and height_match:
        return int(float(width_match.group(1))), int(float(height_match.group(1))), True
    viewbox = re.search(r"\bviewBox=[\"'][^\"']*?([0-9.]+)[ ,]+([0-9.]+)[\"']", text)
    if viewbox:
        return int(float(viewbox.group(1))), int(float(viewbox.group(2))), True
    return None, None, True


def inspect_image(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    extension = path.suffix.lower()
    readers = {".png": png_info, ".jpg": jpeg_info, ".jpeg": jpeg_info, ".gif": gif_info, ".webp": webp_info, ".svg": svg_info}
    if extension not in readers:
        raise AssetError(f"formato não suportado: {extension}")
    width, height, transparent = readers[extension](data)
    ratio = round(width / height, 4) if width and height else None
    return {
        "format": extension.removeprefix(".").replace("jpeg", "jpg"),
        "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": width,
        "height": height,
        "aspect_ratio": ratio,
        "transparent": transparent,
    }


def classify_media(name: str, width: int | None, height: int | None, transparent: bool, size_bytes: int = 0) -> dict[str, Any]:
    normalized = Path(name).stem.lower()
    scores = {role: 0 for role in (*ROLE_WORDS, "unknown")}
    reasons: dict[str, list[str]] = {role: [] for role in scores}
    for role, words in ROLE_WORDS.items():
        matches = [word for word in words if word in normalized]
        if matches:
            scores[role] += 5
            reasons[role].append(f"nome:{matches[0]}")
    ratio = width / height if width and height else None
    if ratio is not None:
        if 0.8 <= ratio <= 1.25:
            scores["logo"] += 2
            scores["portrait"] += 1
            reasons["logo"].append("proporção-quadrada")
        if ratio >= 1.6:
            scores["hero"] += 3
            reasons["hero"].append("proporção-panorâmica")
        if ratio <= 0.8:
            scores["portrait"] += 3
            reasons["portrait"].append("proporção-vertical")
    if transparent:
        scores["logo"] += 3
        reasons["logo"].append("transparência")
    if width and width >= 1400:
        scores["hero"] += 1
        reasons["hero"].append("largura-alta")
    if size_bytes and size_bytes < 400_000 and transparent:
        scores["logo"] += 1
        reasons["logo"].append("arquivo-leve")
    role = max(scores, key=lambda item: scores[item])
    if scores[role] == 0:
        role = "unknown"
    return {"role": role, "score": scores[role], "reasons": reasons[role]}


def inventory(directory: Path) -> list[dict[str, Any]]:
    directory = directory.resolve()
    results = []
    for path in sorted(item for item in directory.rglob("*") if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS):
        try:
            info = inspect_image(path)
            info["path"] = path.relative_to(directory).as_posix()
            info["classification"] = classify_media(path.name, info["width"], info["height"], info["transparent"], info["bytes"])
            results.append(info)
        except AssetError as exc:
            results.append({"path": path.relative_to(directory).as_posix(), "error": str(exc)})
    return results


def assert_public_host(hostname: str) -> None:
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(hostname, None)}
    except socket.gaierror as exc:
        raise AssetError("host não resolvido") from exc
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise AssetError("download para rede local ou reservada recusado")


def download(url: str, destination: Path, max_bytes: int) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise AssetError("somente URL HTTP(S) pública sem credenciais")
    assert_public_host(parsed.hostname)
    request = urllib.request.Request(url, headers={"User-Agent": "landing-page-intake/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        final = urllib.parse.urlparse(response.geturl())
        if final.scheme not in {"http", "https"} or not final.hostname:
            raise AssetError("redirecionamento recusado")
        assert_public_host(final.hostname)
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > max_bytes:
            raise AssetError("arquivo excede limite")
        payload = response.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise AssetError("arquivo excede limite")
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("wb", dir=destination.parent, prefix=".download-", delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {"path": str(destination), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "url": response.geturl()}


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory")
    inv.add_argument("directory", type=Path)
    inv.add_argument("--output", type=Path)
    fetch = commands.add_parser("download")
    fetch.add_argument("url")
    fetch.add_argument("destination", type=Path)
    fetch.add_argument("--max-bytes", type=int, default=10 * 1024 * 1024)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("file", type=Path)
    args = cli.parse_args()
    try:
        if args.command == "inventory":
            result: Any = {"items": inventory(args.directory)}
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif args.command == "download":
            result = download(args.url, args.destination, args.max_bytes)
        else:
            result = inspect_image(args.file)
            result["classification"] = classify_media(args.file.name, result["width"], result["height"], result["transparent"], result["bytes"])
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (AssetError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
