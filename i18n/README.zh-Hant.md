# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

![AgInTi Spectrometer 產品原型](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer 是為 C12880MA 光譜儀設計的高速擷取與視覺化工作臺。單一擷取核心同時支援 Qt 桌面介面、Web 儀表板、CSV 記錄、命令列與 REST API，並將串列擷取和繪圖分離以維持時間解析度。

## 主要功能

- 顯示校準後的 340–850 nm 光譜。
- 支援微秒級至長曝光的固定曝光、自適應曝光及單次測光。
- 原始擷取率與畫面更新率互相獨立。
- 提供暗場扣除、影格平均、濾波、自動量程及原始 CSV 匯出。
- 提供桌面端、瀏覽器與適合代理自動化的 API。

## 快速開始

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

連接儀器後選擇 COM 連接埠並開始擷取。顯示濾波不會覆寫原始資料。

## 支持

[LazyingArt 捐助](https://chat.lazying.art/donate) · [PayPal](https://paypal.me/RongzhouChen) · [Stripe](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
