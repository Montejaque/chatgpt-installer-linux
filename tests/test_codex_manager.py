import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).resolve().parents[1] / "src" / "codex_manager.py"
SPEC = importlib.util.spec_from_file_location("codex_manager", str(MODULE))
manager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manager)

class ReleaseMetadataTests(unittest.TestCase):
    def test_selects_official_linux_x86_64_asset(self):
        release = {"assets": [
            {"name": "codex-aarch64-unknown-linux-musl.tar.gz", "browser_download_url": "https://github.com/openai/codex/releases/download/v1/arm.tar.gz"},
            {"name": "codex-x86_64-unknown-linux-musl.tar.gz", "browser_download_url": "https://github.com/openai/codex/releases/download/v1/codex.tar.gz"}
        ]}
        self.assertEqual(manager.select_linux_asset(release)["name"], manager.ASSET_NAME)

    def test_rejects_untrusted_asset_url(self):
        release = {"assets": [{"name": manager.ASSET_NAME, "browser_download_url": "https://example.invalid/codex.tar.gz"}]}
        with self.assertRaises(RuntimeError):
            manager.select_linux_asset(release)

    def test_rejects_missing_asset(self):
        with self.assertRaises(RuntimeError):
            manager.select_linux_asset({"assets": []})

if __name__ == "__main__":
    unittest.main()
