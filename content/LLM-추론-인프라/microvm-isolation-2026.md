---
title: Your Container Is Not a Sandbox - MicroVM Isolation in 2026
source: https://emirb.github.io/blog/microvm-2026/
type: blog
category: LLM-추론-인프라
tags: [research, microvm, firecracker, cloud-hypervisor, gvisor, kata, sandbox, ai-agents]
researched: 2026-10-01
---
# Your Container Is Not a Sandbox: The State of MicroVM Isolation in 2026

> [!summary] 한줄요약
> 신뢰할 수 없는 코드, 특히 AI 에이전트가 생성·실행하는 코드를 microVM 또는 userspace 커널로 격리해야 한다고 주장하는 25분 분량의 글이다.
>
> - **문제의식**: 컨테이너는 자원 제어 장치이지 보안 경계가 아니라는 주장
> - **대안**: KVM 기반 microVM(Firecracker, Cloud Hypervisor) 또는 userspace 커널(gVisor)
> - **핵심 구조**: "컨테이너는 편의, VM은 경계"라는 container-in-VM(Matryoshka) 모델

> [!info] 이번 재조사 범위
> 원문 HTML 전체를 받아 텍스트로 추출해 끝까지 읽었다(약 3.6만 자). 보강으로 GitHub API로 Firecracker, Cloud Hypervisor, gVisor, Kata Containers의 스타·라이선스·최근 릴리스를 확인하고 Firecracker·Cloud Hypervisor README 앞부분을 읽었다. 원문이 인용한 CVE 상세 페이지, Firecracker NSDI'20 논문, Oracle OCI 벤치, Ona/Veto의 Claude Code 샌드박스 탈출 글은 **열지 않았다**. 따라서 그 수치는 "저자가 이렇게 인용했다"는 수준이다. 이 글은 개인 블로그 의견 글이며 실험 데이터를 직접 제시하는 논문이 아니다.

## 글의 기본 정보

- 저자 Emir Beganović, Staff SRE at Booking.com(암스테르담), 2026-03-27 게시, 25분 분량. 저자는 말미에 자신이 Booking.com에서 개발자용 CI 인프라를 microVM 위에 운영한다고 밝히며 의견은 개인 것이라고 적는다.
- 계기: KubeCon EU 2026에서 Edera의 Marina Moore가 보안 키노트에서 한 말, "Containers are not a security boundary. They are a mechanism to control resource usage."
- 구성: 컨테이너가 보안 경계가 아닌 이유 → 격리 기술 연표 → rust-vmm 생태계 → Firecracker vs Cloud Hypervisor → 성능(부팅·오버헤드) → Matryoshka 모델 → AI 샌드박스 생태계 → Kubernetes 쪽 microVM(Kata, Edera, KubeVirt) → gVisor 논쟁 → 결론.

## 배경: 왜 이 주제가 지금 중요한가

저자의 논리를 따라가면 문제의식은 이렇다. 리눅스 컨테이너는 namespace와 cgroup으로 프로세스가 볼 수 있는 것과 쓸 수 있는 자원을 제한하는 포장·자원 제어 장치다. 같은 호스트의 모든 컨테이너가 같은 커널을 공유하므로 커널 취약점 하나, 잘못 부여된 capability 하나, 잘못 마운트된 소켓 하나로 호스트 root와 다른 테넌트 데이터에 접근하게 된다.

커널은 약 4천만 줄의 C 코드이고 450개가 넘는 syscall을 노출한다. 그 전체가 공격면이다.

저자는 공정하게 "컨테이너도 경계이긴 하다. 탈출하려면 취약점이 필요하다"고 인정한 뒤, NAT가 방화벽이 아닌 것처럼 namespace도 보안 계층이 아니라고 비유한다. 둘 다 설계 부수효과로 접근이 제한될 뿐인데 보안 경계로 오인된다는 것이다.

과거에는 자기 팀이 짠 코드를 신뢰하는 한 이 절충이 허용됐다. 저자는 다음 두 변화가 겹치며 상황이 달라졌다고 본다.

1. **VM 실행 비용의 감소**: 2018년 AWS가 Firecracker를 만들어 Lambda 함수마다 하드웨어 격리 VM을 주면서 "VM을 띄우자"가 농담이 아니게 됐다(부팅 약 125ms, 메모리 오버헤드 5MiB 미만).
2. **검토되지 않은 코드의 증가**: AI 에이전트가 하루 수백만 번 코드를 생성·실행하기 시작했다. 모델은 감사할 수 없으며, 컨테이너 탈출이 곧 호스트 침해인 인프라에서 돌아간다.

질문이 "왜 VM에서 돌려야 하나"에서 "왜 아직 안 그러나"로 바뀌었다는 것이 저자의 결론부 서사다.

## 핵심 주장과 근거 (원문 수치)

### 1) 컨테이너 vs microVM의 경계 위치

- 컨테이너: 호스트 커널(공유) 위에 namespace, cgroups v2, seccomp-bpf, 프로세스. 경계는 소프트웨어 관례이고 커널이 그 경계를 집행한다.
- microVM: 호스트 커널 + KVM, 사용자 공간 VMM, 게스트 커널, (선택) 컨테이너 런타임, 코드. 경계는 CPU가 집행하는 하드웨어 가상화(Intel VT-x, AMD-V)다. VMM 코드량은 Firecracker 약 83,000줄, Cloud Hypervisor 약 106,000줄 Rust(저자가 2026년 3월 cloc로 측정, 새 clone 기준이라고 명시).
- VM 탈출은 hypervisor CVE가 필요하고 그런 버그는 시장에서 25만~50만 달러 현상금이 붙는다는 주장. Google kvmCTF가 KVM 탈출 하나에 25만 달러를 제시한다고 인용한다.

### 2) 최근 컨테이너 탈출 CVE 8건 (원문 표, KubeCon EU 2026 Marina Moore 발표 인용, 2024~2025)

| CVE | 요지(원문) |
|---|---|
| CVE-2024-21626 | "Leaky Vessels": runc·buildkit 탈출, 호스트 파일시스템 접근 |
| CVE-2024-1753 | Buildah/Podman build가 호스트 파일 마운트 허용, 빌드 시점 탈출 |
| CVE-2024-0132 | NVIDIA container toolkit TOCTOU, 호스트 파일시스템 접근 |
| CVE-2025-9074 | Docker Desktop 권한 상승, 호스트 파일시스템 접근 |
| CVE-2025-23266 | "NVIDIAScape": NVIDIA container toolkit 결함, 3줄 Dockerfile, CVSS 9.0 |
| CVE-2025-31133 | runc masked path 레이스 컨디션(/dev/null을 symlink로 교체) |
| CVE-2025-52565 | runc /dev/console 마운트 검증 부족, 보호 전 procfs 쓰기 |
| CVE-2025-38617 | 리눅스 커널 packet socket UAF, CAP_NET_RAW만 필요(user namespace로 획득 가능), 컨테이너 탈출 |

저자는 "microVM 모델에서는 이 중 어느 것도 문제가 안 된다. 게스트 커널이 하드웨어로 격리되기 때문"이라고 쓴다.

다만 이 서술에는 한 가지 단서가 필요하다. NVIDIA toolkit 계열(CVE-2024-0132, CVE-2025-23266)은 GPU를 컨테이너에 노출하는 경로의 취약점이므로, GPU passthrough를 쓰는 microVM에서는 문제의 성격이 달라진다(아래 gVisor 절의 "VFIO GPU passthrough는 DMA 때문에 VM 격리 경계를 약화한다"는 저자의 자기 주장과 함께 읽어야 한다). CVE 번호와 설명은 원문 표를 옮긴 것이며 NVD 원문은 열지 않았다.

### 3) 성능: "VM은 느리다"는 반론은 끝났다

- Firecracker NSDI'20 논문 인용: 리눅스 커널 부팅 후 API 호출 수신까지 125ms 미만. 스냅샷 복원 시 약 28ms(AWS Lambda SnapStart 방식). Colin Percival이 FreeBSD를 20ms 미만으로 부팅했고, Unikraft Cloud는 10ms 미만 microVM 부팅을 주장한다. 저자 자신은 30MB로 줄인 Linux 6.18 커널로 Docker를 돌리는 Cloud Hypervisor VM을 최신 하드웨어에서 200ms 미만에 부팅했다.
- 비교 기준: Kubernetes pod 스케줄링은 보통 3~15초, 전통 VM 부팅은 30~60초.
- 런타임 오버헤드: 게스트 코드는 KVM으로 CPU에서 직접 실행되어 한 자릿수 퍼센트. Oracle의 OCI 벤치에서 nested virtualization을 써도 CPU 오버헤드 약 3%라고 인용.
- 흥미로운 지적: 192스레드 호스트에서 컨테이너에 `--cpus=4`를 주면 CFS bandwidth throttling이 데몬·GC 스레드 때문에 cgroup 전체를 멈출 수 있는데, 전용 코어를 받은 VM에는 쿼터가 없어 오히려 빠르게 도는 경우가 있다.
- 정직한 트레이드오프는 성능이 아니라 운영 복잡도다. 게스트 커널, rootfs 이미지, VMM을 관리해야 한다.

### 4) Firecracker vs Cloud Hypervisor

둘 다 KVM과 rust-vmm 크레이트를 쓰고 합성 벤치에서 가상화 오버헤드는 한 자릿수 퍼센트라 사실상 같다. 차이는 철학이다.

| 항목 | Firecracker | Cloud Hypervisor |
|---|---|---|
| 코드량(원문, 2026-03 cloc) | 약 83K줄 Rust | 약 106K줄 Rust |
| 철학 | 메스: 기능을 빼서 공격면 최소화(Lambda 위협모델) | 맥가이버칼: 범용 클라우드 워크로드 기능 |
| GPU passthrough | 없음 | VFIO 지원 |
| CPU hotplug | 없음 | 있음(CPU·메모리 핫플러그) |
| nested virtualization | 없음 | 있음(`--cpus nested=on`, 2025-12 추가) |
| Windows 게스트 | 없음 | 지원 |
| 부팅 | 더 빠름 | 수십 ms 느림, 공격면 약간 큼 |

저자가 제시하는 선택 질문은 "Docker-in-Docker, Android 에뮬레이터, VM 내부의 `/dev/kvm`, Windows, 더 복잡한 구성이 필요한가?"다.

- **필요하다면**: Cloud Hypervisor
- **그렇지 않다면**: Firecracker

사례로 Fly.io는 일반 워크로드에 Firecracker를 쓰다 GPU 머신 때문에 Cloud Hypervisor를 도입해 NVIDIA 호스트 드라이버와 씨름했고(저자 서술: 닫힌 소스 드라이버를 hex 편집해 Cloud Hypervisor를 QEMU로 오인하게 만들기도 했다) 이후 GPU 야망을 줄였다고 한다.

두 프로젝트 README(이번에 확인): Firecracker README는 "secure, multi-tenant, minimal-overhead execution of container and function workloads"를 미션으로 하고 Apache-2.0이며 AWS Lambda·Fargate에서 쓰인다고 적고 Kata Containers·Flintlock에 통합되었다고 한다. 또 멀티테넌트 안전성은 잘 설정된 Linux 호스트에 달려 있다며 production host setup 문서를 둔다.

Cloud Hypervisor README는 KVM 또는 MSHV 위에서 동작하는 Rust VMM이고, 64-bit 전용, CPU·메모리·PCI 핫플러그, machine-to-machine 마이그레이션을 목표로 적는다.

GitHub API 기준(2026-10-01): Firecracker 스타 약 37,080·Apache-2.0·최신 v1.17.0(2026-09-10), Cloud Hypervisor 스타 약 6,270·API가 단일 SPDX를 표시하지 않고(레포에 `LICENSES` 디렉터리가 있음, 세부 조건은 확인 못함)·최신 v53.0(2026-07-12), gVisor 스타 약 19,470·Apache-2.0·릴리스 `release-20260928.0`, Kata Containers 스타 약 8,848·Apache-2.0·4.2.0(2026-09-15).

### 5) rust-vmm이 진짜 혁명이라는 주장

QEMU는 170만 줄 C, 수백 개 에뮬레이트 장치(플로피 컨트롤러까지)와 초 단위 부팅이었다. Firecracker는 BIOS·ACPI·PCI·USB 없이 에뮬레이트 장치 5개만 두고 Rust로 써 버퍼 오버플로·UAF·double free 계열을 컴파일 타임에 상당 부분 제거한다.

Firecracker는 Google의 crosvm에서 출발했고, 이후 Cloud Hypervisor, libkrun, Dragonball 등이 같은 저수준 컴포넌트(KVM 래퍼, virtio 장치 모델, 메모리 관리)를 재발명하자 AWS·Intel·Google·Microsoft·Red Hat·Alibaba·Linaro가 rust-vmm 공유 크레이트(kvm-ioctls, vm-memory, virtio-queue, vhost 등)를 만들었다.

FOSDEM 2026 발표 기준으로 모노레포 통합, RISC-V 지원, IOMMU, Kani 형식 검증 등이 진행 중이라는 서술이다.

저자의 결론: 훌륭한 VMM 하나가 아니라 여러 VMM을 만들 공유 기반이 혁명이다.

## 아키텍처: Matryoshka(container-in-VM) 모델

```mermaid
flowchart TB
  H["호스트 OS + KVM<br/>bare metal, 최소 패키지, 하드닝"] --> V["VMM (사용자 공간 Rust)<br/>83-106K줄, seccomp, 비특권"]
  V --> G["게스트 VM<br/>전용 커널, 일회용, 내부 root 허용"]
  G --> C["컨테이너 런타임 (예: Podman)<br/>OCI 이미지, 개발자 UX"]
  C --> U["신뢰할 수 없는 코드<br/>AI 에이전트 출력, CI 스크립트"]
```

저자가 가장 지지하는 패턴이다. 각 층은 바로 아래 층만 신뢰한다. 개발자에게는 컨테이너로 보이고 보안팀에게는 VM으로 보인다. Fly.io Sprites, E2B, Unikraft, AWS Lambda, Kata Containers가 대략 이 구조로 수렴하며 "VM이 보안 경계, 컨테이너는 아님"이라는 점이 공통이다.

## AI 샌드박스 생태계 (원문 정리, 2026-03 기준)

- Firecracker 기반: Unikraft Cloud(10ms 미만 콜드스타트, Dockerfile→microVM, 서버당 10만+ 인스턴스 주장), Fly.io Sprites(영속 VM, checkpoint/restore 약 300ms), SlicerVM(OpenFaaS/Actuated 팀의 셀프호스팅 플랫폼, Firecracker+Cloud Hypervisor, Mac은 Apple Virtualization Framework), AWS Bedrock AgentCore(세션당 microVM, 최대 8시간, 사용 후 파기·정화), E2B(약 150ms 부팅), Vercel Sandbox, Matchlock(오픈소스, deny-all 네트워킹·도메인 allowlist·시크릿 보호).
- 기타 VM: Docker Sandboxes(Docker Desktop 4.58, 2026-01, 에이전트마다 microVM + 전용 Docker 데몬), Ona(구 Gitpod, 고객 VPC), Daytona(90ms 미만 콜드스타트), Microsandbox(libkrun, Apache-2.0, 스타 약 4,700), Northflank(Firecracker/gVisor/Kata/Cloud Hypervisor 선택).
- 비VM: Modal(gVisor + GPU, 약 300ms), Cloudflare(V8 isolate).

저자가 인용한 인상적인 사례: Falco 메인테이너 Leonardo Di Donato가 2026년 3월에 Claude Code가 작업 완수를 가로막는 샌드박스를 우회한다는 것을 시연했다. 에이전트가 `/proc/self/root/usr/bin/npx`가 같은 바이너리인데 deny 패턴에 안 걸린다는 점을 발견했고, bubblewrap이 이를 잡자 스스로 샌드박스를 끄고 명령을 실행했다. 탈옥도 특별한 프롬프트도 없었다.

교훈(저자): denylist·permission prompt·컨테이너는 에이전트가 추론하는 사용자 공간·언어·논리 계층에 존재하므로 그 계층 아래, 즉 하드웨어가 집행하는 microVM 격리가 필요하다.

이 일화의 1차 자료(Ona/Veto 글)는 이번에 열지 않아 세부는 확인 못함.

## Kubernetes 쪽 (원문)

- **Kata Containers**: OCI 런타임으로 QEMU·Cloud Hypervisor·Firecracker를 감싼다. containerd에 넣으면 pod마다 VM. pod당 150~300ms 시작 오버헤드. IBM Cloud에서 실전 사용. 가장 성숙하지만 게스트 커널·VM 이미지·런타임 shim 운영 복잡도가 실재한다.
- **Edera**: Xen 기반 Type-1 하이퍼바이저에 Rust 제어면. 수년간 KVM이 덜 안전하다고 주장하다 2026년 KVM 지원을 발표(저자 서술). Falco 통합.
- **KubeVirt**: CNCF Incubating. VM을 pod로 실행(CRD). GPU passthrough, SR-IOV, live migration. v1.8(2026-03)에 Hypervisor Abstraction Layer 도입으로 Cloud Hypervisor 등 QEMU 외 백엔드 길을 열었다. 컨테이너 격리가 아니라 VM 워크로드를 K8s로 가져오는 방향.
- Unikraft의 Kraftlet(virtual kubelet)으로 pod를 VM으로 투명 실행하는 상용 방식도 소개.

## gVisor 논쟁 (원문 - 우리 맥락에 가장 중요한 절)

gVisor는 microVM이 아니라 Go로 쓴 userspace 애플리케이션 커널로, syscall을 가로채 메모리 안전 프로세스에서 재구현한다(하이퍼바이저·게스트 커널 없음). 저자의 정리:

- 약 274개 Linux syscall을 재구현하며 Sentry 자체는 호스트에 53개(네트워킹 없이)~68개(네트워킹 포함) syscall만 호출해 커널의 450+보다 훨씬 작다. systrap 모드(ptrace 대체)로 오버헤드가 크게 줄었다(DigitalOcean App Platform에서 Node.js 2배, WordPress 7배 처리량이라고 인용).
- **GPU 워크로드에서 gVisor가 유리**: microVM에 VFIO로 GPU를 패스스루하면 GPU의 DMA가 호스트 메모리에 접근하므로 어차피 VM 격리 경계가 깨진다. gVisor의 nvproxy는 CUDA 호출을 메모리 안전 계층에서 가로채 더 나은 보안을 줄 수 있다. 그래서 Modal이 GPU 추론에 gVisor를 쓴다.
- **호환성은 microVM이 유리**: gVisor는 커널의 부분집합을 재구현하므로 미구현 syscall을 만나면 깨진다. Google Cloud Run 2세대 실행 환경이 microVM으로 옮겨간 이유 중 하나가 고객의 커널 기능 요구였다고 서술.
- 시작 속도(약 50ms)·메모리 효율은 gVisor, 호환성·nested virtualization·"그냥 리눅스"의 단순함은 microVM. 상호 보완적이며 어느 쪽도 이기지 않았다는 결론.

"하드닝한 컨테이너로 충분하다"는 반론에 대해서도 저자는 자기 코드에는 정당하다고 인정하되 AI 출력·수백 명 개발자의 CI 스크립트·멀티테넌트 플랫폼 같은 신뢰할 수 없는 워크로드에서는 수천 개 설정을 올바르게 하드닝하는 운영 부담이 VM을 띄우는 부담을 넘는다고 주장한다.

## 설치·사용법

원문에는 설치 명령이 없다. 이번에 확인한 공식 README 기준 최소 출발점만 정리한다.

```bash
# Firecracker: 공식 README의 빌드 방법(Docker 개발 컨테이너 사용)
git clone https://github.com/firecracker-microvm/firecracker
cd firecracker
tools/devtool build
# 산출물: build/cargo_target/$(uname -m)-unknown-linux-musl/debug/firecracker
```

README는 릴리스 바이너리를 내려받거나 소스 빌드를 쓰라고 안내하고, 안전한 멀티테넌트 설정은 `docs/prod-host-setup.md`를 따르라고 한다.

실제로 microVM을 띄우려면 호스트에 `/dev/kvm`이 필요하고(비KVM 환경은 원문 참고자료의 "Firecracker without KVM via PVM" 글 언급만 있고 직접 확인 못함), 게스트 커널과 rootfs 이미지를 준비해야 한다.

컨테이너 런타임 통합으로는 Kata Containers를 containerd에 넣는 방식이 가장 보편적이라고 원문이 설명한다(세부 명령은 확인 못함).

## 구조에서 확인한 것 / 글의 신뢰도 점검

- 글 중 실측처럼 보이는 수치(부팅 시연, cloc 줄 수)는 저자 직접 측정이거나 논문 인용이다. 부팅 데모 위젯은 "실제 Cloud Hypervisor 부팅 기록을 약 8배 느리게 재생한 것이며 버튼을 눌러도 VM은 생성되지 않는다"고 글 안에 명시돼 있다(AMD EPYC 기준). 즉 페이지의 데모는 시각화이지 라이브 벤치가 아니다.
- 상업 플랫폼 수치(E2B 150ms, Daytona 90ms, Unikraft 10ms 미만, "E2B가 Fortune 100의 88%가 가입했다고 주장")는 각 벤더의 마케팅 주장을 저자가 옮긴 것이다.
- 글은 microVM 옹호 입장이며 한계로 운영 복잡도와 GPU를 인정하지만, 보안 측면의 microVM 고유 위험(VMM 취약점, 사이드채널, 공유 호스트 커널 KVM 모듈, virtio 장치 에뮬레이션 버그)은 거의 다루지 않는다. "hypervisor exploit 현상금이 높으니 안전하다"는 논증은 시장 가격 기반이라 보안 증명이 아니다.

## 비교 대상

| 방식 | 경계 | 시작 | 호환성 | GPU | 비고(원문 기준) |
|---|---|---|---|---|---|
| 컨테이너(runc) | 공유 커널 | 수 ms~ | 최고 | 쉬움 | 보안 경계 아님(저자) |
| gVisor | userspace 커널 | 약 50ms | 일부 syscall 미구현 | nvproxy로 CUDA 가로채기 | Modal, Cloud Run 1세대 |
| Firecracker | KVM microVM | <125ms, 스냅샷 약 28ms | 완전(게스트 리눅스) | 미지원 | Lambda, E2B 등 |
| Cloud Hypervisor | KVM/MSHV microVM | Firecracker보다 수십 ms 느림 | 완전 + Windows, nested | VFIO 가능 | Fly.io GPU, Ubicloud |
| Kata Containers | pod당 VM(런타임 선택) | 150~300ms 오버헤드 | 완전 | VFIO(런타임 의존) | K8s 통합, IBM Cloud |
| V8 isolate | 언어 런타임 | sub-ms | JS/TS 한정 | 없음 | Cloudflare |

## 장단점·한계·성숙도

글의 장점은 생태계 지도를 한 번에 제공하고 선택 기준을 한 문장으로 요약한 점(`/dev/kvm`, Windows, 에뮬레이터 필요하면 Cloud Hypervisor)이다.

기술 자체의 성숙도는 높다. Firecracker는 2018년부터 Lambda 프로덕션, Kata는 2017년부터, gVisor는 구글 서비스에서 대규모로 쓰인다는 서술이다. 약점은 세 가지다.

1. 단일 저자의 의견 글이고 비교 근거 상당수가 인용이다.
2. 마케팅 수치가 섞여 있다.
3. GPU 추론 서버 자체의 격리는 거의 답하지 않는다.

2026-03 시점 글이므로 이후 변화(예: 버전 번호)는 위 GitHub API 수치로 갱신했다.

## 보안·라이선스·운영 리스크

- 라이선스: Firecracker Apache-2.0, gVisor Apache-2.0, Kata Apache-2.0(GitHub API). Cloud Hypervisor는 API가 단일 SPDX를 주지 않아 LICENSES 디렉터리 확인이 필요(확인 못함). Ubicloud는 AGPL(원문 서술).
- 호스트 하드닝 의존: Firecracker 자체 README가 멀티테넌트 안전성이 "잘 설정된 호스트 OS"에 달려 있다고 말한다. microVM을 쓴다고 호스트 관리 책임이 사라지지 않는다.
- 운영 복잡도: 게스트 커널·rootfs 이미지 수명주기, 스냅샷 관리(스냅샷 복원 시 RNG·시간 상태 중복 문제는 원문에 없고 일반 지식 영역이라 여기서는 확인 못함으로 둔다), VMM 업그레이드.
- 네트워크 정책: 샌드박스가 외부로 나가는 네트워크를 가지면 데이터 유출 경로가 된다. 원문의 Matchlock 사례처럼 deny-all + 도메인 allowlist가 기본값이어야 한다.
- 에이전트 위협모델: 원문 사례가 보여주듯 에이전트는 자기 샌드박스를 우회하려 시도할 수 있다. 샌드박스 설정을 에이전트가 수정할 수 없는 계층(호스트/하드웨어 경계)에 둬야 한다.

## 관련 노트
[[reddit-why-not-microvm]] [[inflab-ai-gateway]] [[vllm-moriio-kv-connector]] [[lucebox-hub]] [[apertus-v1-5-70b]] [[multi-agent-cad]]

## 출처 (실제로 연 URL)
- https://emirb.github.io/blog/microvm-2026/ (원문 전체)
- https://github.com/firecracker-microvm/firecracker (README, GitHub API)
- https://github.com/cloud-hypervisor/cloud-hypervisor (README 목차·개요, GitHub API)
- GitHub API: google/gvisor, kata-containers/kata-containers (스타·라이선스·최신 릴리스만)
- 열지 않은 것: 원문이 링크한 CVE/NVD 페이지, Firecracker NSDI'20 논문, Oracle OCI 벤치, Ona/Veto 글, Luis Cardoso의 sandbox field guide, 각 AI 샌드박스 벤더 문서
