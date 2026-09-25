import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

script = Path(__file__).with_name("verify-native-package.py")
spec = importlib.util.spec_from_file_location("verify_native_package", script)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

class ArchiveVerification(unittest.TestCase):
    def test_changed_packaged_source_is_rejected(self):
        manifest = {"schema": 1, "native_commit": "fixture", "files": {"libssh2/src/transport.c": verify.digest(b"expected source")}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.crate"
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("fixture/libssh2/src/transport.c")
                data = b"different source"
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            with self.assertRaisesRegex(AssertionError, "packaged source differs"):
                verify.verify_archive(path, manifest)

    def test_missing_native_file_is_rejected(self):
        manifest = {"files": {"libssh2/src/transport.c": "missing"}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.crate"
            with tarfile.open(path, "w:gz") as archive:
                data = b"{}"
                info = tarfile.TarInfo("fixture/NATIVE-SOURCE.json")
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            with self.assertRaisesRegex(AssertionError, "native file set differs"):
                verify.verify_archive(path, manifest)

if __name__ == "__main__":
    unittest.main()
