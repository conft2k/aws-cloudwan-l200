# ws-aws-cloudwan-l200

AWS Cloud WAN L200 워크숍입니다. 이론 1시간(별도 저장소 `conft2k/deck-aws-cloudwan`의 deck), 실습 1시간입니다.

계획과 설계 결정은 [PLAN.md](PLAN.md)에 있습니다. 시나리오, 주소·ASN 설계, 세그먼트 설계, 과제 표, 시간 배분, 사전 테스트 기록이 모두 거기 있습니다. **작업 전에 PLAN.md를 먼저 읽으세요.**

## 집필 규칙

- 번호 체계: 묶음 `2.`, 페이지 `2-2.`, 소절 `2-2-a.`. 소절마다 `{ #lab1-a }` 형태의 앵커를 답니다. 자세한 것은 PLAN.md 11-1절.
- 쉬운 한국어 존댓말. 처음 나오는 약어는 풀어 씁니다.
- 콘솔 UI 이름은 영어 그대로 굵게, 경로는 `→`로 잇습니다. 입력값과 JSON 키는 백틱.
- 세그먼트 이름은 정책 JSON에 적는 그대로 소문자: `prod`, `dev`, `shared`, `onprem`.
- 소절 끝마다 `**성공 확인**: …` 한 줄. 실패가 정상인 단계는 `**결과(실패가 맞습니다)**`로 미리 알립니다.
- **콘솔 조작 순서는 직접 실행해 본 것만 적습니다.** 버튼 이름과 위치를 코드나 문서에서 짐작하지 않습니다. 확인하지 못한 것은 추측해 쓰지 말고 남겨 두고 보고합니다.
- 측정하지 않은 소요 시간을 지어내지 않습니다. "사전 테스트에서 측정합니다"로 둡니다.

## 구성도

`docs/images/**/*.draft.svg`는 `tools/diagrams/`의 생성기 스크립트가 만듭니다. draft를 직접 고치지 말고 스크립트를 고친 뒤 다시 만드세요.

```bash
tools/diagrams/build.sh --check    # 스크립트 결과가 저장소의 draft와 같은지 확인
tools/diagrams/build.sh segments   # 하나만 다시 만들기
```

구성도는 [skill-aws-arch-diagram](https://github.com/conft2k/skill-aws-arch-diagram)의 공식 AWS Architecture Icons로만 만듭니다. 손으로 그린 비슷한 아이콘이나 텍스트 칩을 쓰지 않습니다.

## 스크린샷

`tools/console.py`가 Playwright로 영어 콘솔을 조작해 `shots/raw/`에 원본을 남기고, `shots/crop.py`가 `docs/images/console/`로 잘라 넣습니다. 계정 ID는 `111122223333`으로 가립니다.

```bash
AWS_PROFILE=cwan uv run --with playwright --with boto3 python tools/console.py <script.py>
uv run --with pillow python shots/crop.py
```

## AWS

- 테스트 계정은 `cwan` 프로필입니다. 명령마다 `--profile cwan`을 명시합니다.
- 실습 리전은 서울 `ap-northeast-2`와 오레곤 `us-west-2` 두 곳입니다. 명령마다 `--region`을 명시합니다.
- CloudFormation 템플릿은 배포 전에 cfn-lint로 검증합니다.
- **core network edge는 리전당 시간당 요금이 붙습니다.** 검증이 끝나면 PLAN.md 10절 순서대로 정리하세요.

## 사이트

mkdocs-material로 빌드해 GitHub Pages로 <https://ws.nettfc.net/ws-aws-cloudwan-l200/>에 올립니다. `main`에 push하면 `.github/workflows/pages.yml`이 배포합니다.

```bash
uv run --with mkdocs-material==9.8.0 mkdocs serve
uv run --with mkdocs-material==9.8.0 mkdocs build --strict
```

`docs/agents/`는 `exclude_docs`로 사이트에서 빠집니다.

## Agent skills

### Issue tracker

이슈는 이 저장소의 GitHub Issues에 둡니다(`gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

기본 라벨 다섯 가지를 그대로 씁니다(`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

single-context입니다(저장소 루트의 `GLOSSARY.md`와 `docs/adr/`). See `docs/agents/domain.md`.
