# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

![AgInTi Spectrometer 製品プロトタイプ](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer は C12880MA 用の高速取得・可視化ワークベンチです。単一の取得コアから Qt デスクトップ、Web ダッシュボード、CSV 記録、CLI、REST API を提供し、シリアル取得と描画を分離して時間分解能を維持します。

## 主な機能

- 校正済み 340–850 nm スペクトル表示。
- マイクロ秒から長時間露光までの固定、自動、ワンショット測光。
- 取得レートと画面更新レートを独立制御。
- ダーク補正、平均化、フィルタ、自動レンジ、Raw CSV 出力。
- デスクトップ、Web、エージェント向け API。

## クイックスタート

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

装置を接続し、COM ポートを選択して取得を開始します。表示フィルタは記録された生データを変更しません。

## サポート

<!-- support:start -->
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)
[![LazyingArt Support](https://img.shields.io/badge/LazyingArt-Support-0EA5E9?style=for-the-badge)](https://chat.lazying.art/donate)
[![PayPal Support](https://img.shields.io/badge/PayPal-Support-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen)
[![Stripe Support](https://img.shields.io/badge/Stripe-Support-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
<!-- support:end -->
