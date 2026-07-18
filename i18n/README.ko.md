# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

![AgInTi Spectrometer 제품 프로토타입](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer는 C12880MA용 고속 수집 및 시각화 워크벤치입니다. 하나의 수집 코어가 Qt 데스크톱, 웹 대시보드, CSV 기록, CLI와 REST API를 제공하며, 직렬 수집과 렌더링을 분리해 시간 해상도를 유지합니다.

## 주요 기능

- 보정된 340–850 nm 스펙트럼 표시.
- 마이크로초부터 장노출까지 고정, 자동, 일회 측광.
- 원시 수집 속도와 화면 갱신 속도의 독립 제어.
- 다크 프레임 보정, 평균화, 필터, 자동 범위, 원시 CSV 내보내기.
- 데스크톱, 웹, 에이전트 자동화용 API.

## 빠른 시작

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

장치를 연결하고 COM 포트를 선택한 뒤 수집을 시작합니다. 표시 필터는 기록된 원시 샘플을 변경하지 않습니다.

## 후원

[LazyingArt](https://chat.lazying.art/donate) · [PayPal](https://paypal.me/RongzhouChen) · [Stripe](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
