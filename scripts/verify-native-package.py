"""Verify the actual bundled native files against the pinned source manifest."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "libssh2-sys/NATIVE-SOURCE.json"

def digest(data):
    # Git checkouts may use CRLF on Windows. No other transformation is allowed.
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()

def verify_source(manifest):
    native = ROOT / "libssh2-sys/libssh2"
    head = subprocess.check_output(["git", "-C", str(native), "rev-parse", "HEAD"], text=True).strip()
    assert head == manifest["native_commit"], "native submodule revision drift"
    for path, expected in manifest["files"].items():
        assert path.startswith("libssh2/") and ".." not in Path(path).parts
        current = ROOT / "libssh2-sys" / path
        original = subprocess.check_output(["git", "-C", str(native), "show", f"{head}:{path.removeprefix('libssh2/')}"])
        assert digest(original) == expected, f"manifest does not match pinned git object: {path}"
        assert digest(current.read_bytes()) == expected, f"working source changed: {path}"

def verify_archive(path, manifest):
    with tarfile.open(path) as archive:
        roots = {member.name.split("/")[0] for member in archive.getmembers()}
        assert len(roots) == 1
        prefix = roots.pop() + "/"
        actual = {member.name.removeprefix(prefix) for member in archive.getmembers()
                  if member.isfile() and member.name.startswith(prefix + "libssh2/")}
        assert actual == set(manifest["files"]), f"native file set differs: {actual ^ set(manifest['files'])}"
        for filename, expected in manifest["files"].items():
            member = archive.getmember(prefix + filename)
            assert member.isfile(), filename
            assert digest(archive.extractfile(member).read()) == expected, f"packaged source differs: {filename}"
        embedded = json.load(archive.extractfile(prefix + "NATIVE-SOURCE.json"))
        assert embedded == manifest, "packaged provenance manifest differs"
        for license_file in ("LICENSE-MIT", "LICENSE-APACHE", "libssh2/COPYING"):
            assert archive.getmember(prefix + license_file).size > 100, license_file
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    verify_source(manifest)
    result = {"native_commit": manifest["native_commit"], "native_files": len(manifest["files"]), "source": "verified"}
    if args.archive:
        result["archive_sha256"] = verify_archive(args.archive, manifest)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
