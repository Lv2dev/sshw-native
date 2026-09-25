# sshw-libssh2-sys

이 저장소는 SSHW 배포를 위한 `sshw-ssh2`와 `sshw-libssh2-sys`를 관리합니다. Rust API crate 이름은 `ssh2`/`libssh2_sys`이며 원본 프로젝트가 게시한 패키지와 구분되는 별도 배포물입니다.

- Rust bindings: rust-lang/ssh2-rs `a014f9ab41809a5bce7e1bea6139464e229d2aac`
- Bundled C library: libssh2/libssh2 `4aded1bf2de0a7ceb02cd50b0b1f7a826984783a` (1.11.2 development snapshot)
- 시스템 libssh2나 vcpkg libssh2를 자동 선택하지 않습니다. 각 패키지는 고정된 native 소스를 사용합니다.
- `libssh2-sys/NATIVE-SOURCE.json`과 `scripts/verify-native-package.py`로 실제 배포 archive의 native 파일을 검증합니다.
- 새 native snapshot은 security patch 포함·3OS build·ABI·실SSH 검증 후에만 갱신합니다. 공식 패키지가 요구되는 수정과 검증을 충족하면 공식 dependency 복귀를 검토합니다.

```toml
[dependencies]
ssh2 = { package = "sshw-ssh2", version = "0.1.0" }
```

현재 bundled libssh2는 upstream의 1.11.2 개발 snapshot이므로 1.11.1과 기본 알고리즘 지원이 다를 수 있습니다. 배포 전에 지원하는 서버와 연결·인증·전송을 검증해야 합니다.

## 출처와 라이선스

Rust bindings는 원본의 MIT 또는 Apache-2.0 조건을 유지합니다. bundled libssh2는 해당 COPYING의 BSD-3-Clause 조건을 따릅니다. 원본 copyright와 license 파일을 그대로 포함합니다. 이 배포물에 대한 upstream 저자의 보증이나 승인을 의미하지 않습니다.

## 검증과 게시 순서

1. submodule을 위 commit으로 초기화합니다.
2. `cargo build --workspace`, `cargo test --lib`, `cargo run -p systest`로 build/API/ABI를 확인합니다.
3. `cargo package -p sshw-libssh2-sys` 후 `python scripts/verify-native-package.py <crate-path>`를 실행합니다.
4. 실제 SSHW 및 원격 SSH fixture에서 연결·인증·전송·권한 상승을 확인합니다.
5. native sys package를 먼저 게시하고 registry checksum을 검증한 뒤 wrapper package를 게시합니다. SSHW는 두 package의 registry 버전을 사용하며 로컬 patch override를 배포하지 않습니다.
