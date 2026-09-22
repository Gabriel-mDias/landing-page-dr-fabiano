from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import asset_utils  # noqa: E402
import workflow  # noqa: E402


class ManifestCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.assets = Path(self.temporary.name) / ".assets"
        self.env = {**os.environ, "LP_ASSETS_DIR": str(self.assets), "PYTHONUTF8": "1"}
        self.run_cli("init", "acme", "--display-name", "ACME")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def manifest_path(self) -> Path:
        return self.assets / "acme" / "manifest.json"

    def run_cli(self, *arguments: str, expect: int = 0) -> dict:
        process = subprocess.run(
            [sys.executable, str(SCRIPTS / "manifest.py"), *arguments],
            cwd=ROOT,
            env=self.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(process.returncode, expect, process.stderr or process.stdout)
        stream = process.stdout if expect == 0 else process.stderr
        return json.loads(stream)

    def patch(self, owner: str, data: dict, expect: int = 0) -> dict:
        patch_path = Path(self.temporary.name) / f"{owner}.json"
        patch_path.write_text(json.dumps(data), encoding="utf-8")
        return self.run_cli("patch", "acme", owner, str(patch_path), expect=expect)

    def read(self) -> dict:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def test_init_and_validate(self) -> None:
        result = self.run_cli("validate", "acme")
        self.assertTrue(result["ok"])
        self.assertEqual(self.read()["schema_version"], "1.0")
        self.assertTrue((self.assets / "acme" / "instagram" / "candidates").is_dir())

    def test_get_by_dotted_path(self) -> None:
        result = self.run_cli("get", "acme", "entity.display_name")
        self.assertEqual(result["value"], "ACME")

    def test_merge_preserves_other_sections(self) -> None:
        before = self.read()["web"]
        self.patch("instagram", {"instagram": {"handle": "@acme"}})
        after = self.read()
        self.assertEqual(after["instagram"]["handle"], "@acme")
        self.assertEqual(after["web"], before)

    def test_rejects_patch_outside_ownership(self) -> None:
        before = self.manifest_path.read_bytes()
        error = self.patch("instagram", {"contact": {"email": "x@example.com"}}, expect=2)
        self.assertIn("não pode escrever", error["error"])
        self.assertEqual(self.manifest_path.read_bytes(), before)

    def test_invalid_patch_preserves_original(self) -> None:
        before = self.manifest_path.read_bytes()
        error = self.patch("landing_page", {"landing_page": {"output_paths": ["../escape.html"]}}, expect=2)
        self.assertIn("caminho", error["error"])
        self.assertEqual(self.manifest_path.read_bytes(), before)

    def test_rejects_unmasked_document_and_unsafe_path(self) -> None:
        data = self.read()
        data["entity"]["document"] = {"type": "cpf", "value": "123.456.789-00"}
        data["web"]["profile_path"] = "C:/private/file.json"
        self.manifest_path.write_text(json.dumps(data), encoding="utf-8")
        error = self.run_cli("validate", "acme", expect=2)
        self.assertIn("mascarado", error["error"])
        self.assertIn("caminho inseguro", error["error"])

    def test_conflict_registration(self) -> None:
        observed = "2026-09-18T12:00:00Z"
        conflict = {
            "field": "contact.phone",
            "values": [
                {"value": "+551100000001", "source": "site oficial", "url": "https://example.com", "observed_at": observed},
                {"value": "+551100000002", "source": "Maps", "url": "https://maps.google.com", "observed_at": observed},
            ],
            "status": "open",
        }
        self.patch("web", {"conflicts": [conflict]})
        self.assertEqual(self.read()["conflicts"][0]["field"], "contact.phone")


class WorkflowTests(unittest.TestCase):
    def base_manifest(self) -> dict:
        data = json.loads((ROOT / "contracts" / "manifest.template.json").read_text(encoding="utf-8"))
        data["entity"]["id"] = "acme"
        data["entity"]["display_name"] = "ACME"
        stamp = "2026-09-18T12:00:00Z"
        data["created_at"] = data["updated_at"] = stamp
        return data

    def set_cache(self, data: dict, domain: str, collected: datetime, expires: datetime) -> None:
        data["intake_status"][domain] = "ready"
        data["cache"][domain] = {
            "fingerprint": f"{domain}-hash",
            "collected_at": collected.isoformat(),
            "expires_at": expires.isoformat(),
        }

    def ready_manifest(self, now: datetime) -> dict:
        data = self.base_manifest()
        for domain in ("instagram", "web"):
            self.set_cache(data, domain, now, now + timedelta(days=1))
        data["intake_status"]["media"] = "ready"
        return data

    def test_cache_valid_expired_and_selective_refresh(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        data = self.base_manifest()
        self.set_cache(data, "instagram", now - timedelta(hours=1), now + timedelta(hours=23))
        self.set_cache(data, "web", now - timedelta(days=8), now - timedelta(days=1))
        self.assertEqual(workflow.cache_state(data, "instagram", now), "valid")
        self.assertEqual(workflow.cache_state(data, "web", now), "stale")
        plan = workflow.build_plan(data, refresh_instagram=True, now=now)
        self.assertIn("collect_instagram", plan["actions"])
        self.assertIn("collect_web", plan["actions"])
        self.assertNotIn("run_builder", plan["actions"])
        self.assertTrue(plan["requires_replan"])
        data["cache"]["web"]["expires_at"] = (now + timedelta(days=1)).isoformat()
        plan = workflow.build_plan(data, refresh_instagram=True, now=now)
        self.assertIn("collect_instagram", plan["actions"])
        self.assertNotIn("collect_web", plan["actions"])

    def test_instagram_ready_web_stale(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        data = self.base_manifest()
        self.set_cache(data, "instagram", now, now + timedelta(hours=24))
        self.set_cache(data, "web", now - timedelta(days=8), now - timedelta(days=1))
        plan = workflow.build_plan(data, now=now)
        self.assertEqual(plan["actions"], ["collect_web", "replan"])
        self.assertEqual(plan["stage"], "intake")

    def test_existing_only_stops_when_data_missing(self) -> None:
        plan = workflow.build_plan(self.base_manifest(), existing_only=True)
        self.assertNotIn("collect_instagram", plan["actions"])
        self.assertNotIn("run_builder", plan["actions"])
        self.assertEqual(plan["actions"][-1], "stop_existing_data_insufficient")

    def test_existing_only_runs_builder_with_valid_cache(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        data = self.ready_manifest(now)
        plan = workflow.build_plan(data, existing_only=True, now=now)
        self.assertEqual(plan["actions"], ["validate_manifest", "run_builder"])
        self.assertTrue(plan["builder_ready"])

    def test_open_conflict_blocks_builder(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        data = self.ready_manifest(now)
        data["conflicts"] = [{"status": "open"}]
        plan = workflow.build_plan(data, now=now)
        self.assertIn("open_conflicts", plan["blockers"])
        self.assertFalse(plan["builder_ready"])
        self.assertNotIn("run_builder", plan["actions"])

    def test_partial_intake_requires_collection_and_replan(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        data = self.ready_manifest(now)
        data["intake_status"]["instagram"] = "partial"
        plan = workflow.build_plan(data, now=now)
        self.assertEqual(plan["actions"], ["collect_instagram", "replan"])
        self.assertIn("intake_instagram_partial", plan["blockers"])

    def test_media_evaluation_is_independent_of_asset_authorization(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        data = self.ready_manifest(now)
        data["instagram"]["authorization"] = "unknown"
        self.assertTrue(workflow.build_plan(data, now=now)["builder_ready"])
        data["intake_status"]["media"] = "pending"
        plan = workflow.build_plan(data, now=now)
        self.assertIn("media_pending", plan["blockers"])
        self.assertNotIn("run_builder", plan["actions"])

    def test_full_refresh_collects_both_then_replans(self) -> None:
        now = datetime(2026, 9, 18, 15, tzinfo=timezone.utc)
        plan = workflow.build_plan(self.ready_manifest(now), refresh=True, now=now)
        self.assertEqual(plan["actions"], ["collect_instagram", "collect_web", "replan"])
        self.assertEqual(plan["refresh"], {"instagram": True, "web": True})

    def test_existing_only_reports_every_blocker(self) -> None:
        data = self.base_manifest()
        data["conflicts"] = [{"status": "open"}]
        plan = workflow.build_plan(data, existing_only=True)
        self.assertEqual(plan["stage"], "blocked")
        self.assertEqual(plan["gaps"], ["instagram:missing", "web:missing"])
        self.assertIn("media_pending", plan["blockers"])
        self.assertIn("open_conflicts", plan["blockers"])


class AssetTests(unittest.TestCase):
    def test_heuristic_image_classification(self) -> None:
        logo = asset_utils.classify_media("logo-marca.png", 600, 600, True, 120_000)
        hero = asset_utils.classify_media("capa-principal.jpg", 1920, 800, False, 900_000)
        portrait = asset_utils.classify_media("retrato-fundadora.jpg", 800, 1200, False, 500_000)
        self.assertEqual(logo["role"], "logo")
        self.assertEqual(hero["role"], "hero")
        self.assertEqual(portrait["role"], "portrait")


if __name__ == "__main__":
    unittest.main()
