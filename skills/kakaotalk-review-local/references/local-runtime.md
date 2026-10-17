# 로컬 실행

Ollaya는 런타임, Laya multilingual은 모델이다. Python 도우미는 Python 3.9+ 표준 라이브러리만 사용하며 Ollaya 서버 설치를 대신하지 않는다.

공식 [다운로드](https://ollaya.dev/download)에서 사용자 OS용 배포를 확인한다. macOS 공식 요구 사항은 Apple Silicon + macOS 14 이상이다. 검증용 폴더 설치는 시스템 PATH·로그인 시작 항목을 바꿀 필요가 없다. 공식 릴리스와 SHA256을 확인한다. 모델/로그 저장 위치도 실행 폴더로 지정할 수 있다.

```bash
OLLAYA_HOST=127.0.0.1:11435 OLLAYA_THREADS=4 OLLAYA_MAX_LOADED_MODELS=1 OLLAYA_KEEP_ALIVE=2m ollaya serve
ollaya pull laya:multilingual
```

기존 같은 포트의 서버가 있으면 먼저 `/api/version`, `/api/tags`, `/api/ps`로 식별한다. 원격 주소에 채팅을 보내지 않는다. 로컬 포트가 실행 파일의 신원을 보증하는 것은 아니므로 사용자가 신뢰하는 Ollaya 인스턴스인지 확인한다. 인증이 필요한 기존 서버는 임의로 인증을 해제하지 말고 별도 실행 설정을 협의한다. 현재 도우미에는 인증 헤더 기능이 없다.

- `laya` 라우터 대신 `laya:multilingual`만 내려받아 영어 모델의 불필요한 상주를 피한다.
- 짧은 대화 묶음부터 시작한다. 큰 문서·많은 동시 요청·자동 재시도는 자원 사용과 대기를 늘릴 수 있다.
- 모델 다운로드 크기와 실제 RSS·CPU를 구분한다. CPU 스레드 4개는 시작 설정이지 최적 설정이 아니다.
- API 응답의 `state_truncated`가 없거나 참이면 해당 결과를 사용하지 않는다. 긴 입력은 Codex가 의미 단위로 나누거나 직접 검토하고, 누락 없이 다시 연결한다.
- 결과 파일은 배타적으로 생성하며 기존 파일을 덮어쓰지 않는다. 실행 폴더는 공개 Git 추적 밖에 두고 원문·모델·결과·로그를 업로드하지 않는다.
- 테스트로 시작한 서버만 끝나면 종료하고, 기존 사용자 서버는 종료하지 않는다. 2분 keep-alive는 언로드 정책이며 프로세스 종료는 아니다.

공식 사양: [Quickstart](https://ollaya.dev/docs/quickstart), [API](https://ollaya.dev/docs/api), [Laya 배포](https://ollaya.dev/library/laya), [모델 한계](https://github.com/NandhaKishorM/laya#honest-limits).
