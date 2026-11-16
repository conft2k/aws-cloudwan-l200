# AWS Cloud WAN 워크숍 (L200)

운영(prod)·개발(dev)·공유(shared) 환경과 온프레미스를 AWS Cloud WAN 하나로 글로벌 연결하는 2시간 워크숍입니다. 이론 1시간, 실습 1시간입니다.

사이트: <https://ws.nettfc.net/ws-aws-cloudwan-l200/>

## 이 저장소에 있는 것

| 경로 | 내용 |
|---|---|
| `PLAN.md` | 계획서. 시나리오, 주소·ASN 설계, 과제 표, 시간 배분, 사전 테스트 기록 |
| `docs/` | 워크숍 사이트 본문 (mkdocs-material) |
| `docs/assets/cloudwan-workshop-seoul.yaml` | 서울 리전 실습 스택 |
| `docs/assets/cloudwan-workshop-oregon.yaml` | 오레곤 리전 실습 스택 |
| `docs/images/` | 구성도와 콘솔 스크린샷 |
| `tools/diagrams/` | 구성도 생성 스크립트 |
| `tools/console.py` | Playwright로 영어 콘솔을 조작해 스크린샷을 찍는 도구 |
| `shots/` | 스크린샷 crop 설정과 스크립트 |

## 페이지 번호

| 묶음 | 페이지 | 파일 |
|---|---|---|
| 1. 시작하기 전에 | 1-1 소개 | `docs/index.md` |
| | 1-2 사전 준비 | `docs/prerequisites.md` |
| | 1-3 용어 풀이 | `docs/glossary.md` |
| 2. 실습 | 2-1 시작하기 | `docs/lab0.md` |
| | 2-2 세그먼트와 글로벌 연결 | `docs/lab1.md` |
| | 2-3 온프레미스 연결 | `docs/lab2.md` |
| | 2-4 정책으로 통신 범위 바꾸기 | `docs/lab3.md` |
| 3. 추가 과제 | 3-1 연결 승인과 격리 옵션 | `docs/extra-a.md` |
| | 3-2 Transit Gateway와 비교 | `docs/extra-b.md` |
| | 3-3 경로 테이블과 지표 보기 | `docs/extra-c.md` |
| | 3-4 리소스 정리 | `docs/extra-d.md` |
| 4. 부록 | 4-1 core network policy 읽는 법 | `docs/concepts.md` |
| | 4-2 Direct Connect로 연결할 때 | `docs/direct-connect.md` |
| | 4-3 문제 해결 | `docs/troubleshooting.md` |
| | 4-4 참고 문서 | `docs/references.md` |

소절은 `2-2-a`처럼 영문 소문자를 붙입니다.

## 로컬에서 보기

```bash
uv run --with mkdocs-material==9.8.0 mkdocs serve
```

## 구성도 다시 만들기

```bash
tools/diagrams/build.sh --check        # 스크립트 결과가 저장소의 draft와 같은지 확인
tools/diagrams/build.sh architecture   # 하나만 다시 만들기
tools/diagrams/build.sh                # 전부
```

구성도는 [skill-aws-arch-diagram](https://github.com/conft2k/skill-aws-arch-diagram)의 공식 AWS Architecture Icons로 만듭니다. `docs/images/**/*.draft.svg`를 직접 고치지 말고 `tools/diagrams/`의 스크립트를 고치세요.

## 이론 자료

이론 1시간은 별도 저장소의 deck을 씁니다: `conft2k/deck-aws-cloudwan` (슬라이드 49장, 약 50분).

## 다른 리전에서 진행할 때

이 워크숍은 서울 `ap-northeast-2`와 오레곤 `us-west-2`를 씁니다. 두 템플릿 모두 리전을 고정(`Rules`)하고 있습니다. 다른 리전으로 바꾸려면 템플릿의 리전 규칙, core network policy의 `edge-locations`와 edge ASN, 콘솔 스크린샷을 함께 고쳐야 합니다.

## 라이선스

MIT. 자세한 내용은 [LICENSE](LICENSE)를 보세요.
