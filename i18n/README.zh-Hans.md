# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

![AgInTi Spectrometer 产品原型](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer 是面向 C12880MA 光谱仪的高速采集与可视化工作台。统一采集核心同时服务于 Qt 桌面端、Web 界面、CSV 记录、命令行和 REST API，并将串口采集与绘图解耦，以保持较高时间分辨率。

## 主要功能

- 显示标定后的 340–850 nm 光谱。
- 支持微秒级到长曝光的固定曝光、自适应曝光和单次测光。
- 原始采集速率与界面刷新速率独立。
- 支持暗场扣除、帧平均、滤波、自动量程和原始 CSV 导出。
- 提供桌面端、浏览器界面和便于智能体调用的 API。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

连接设备后选择 COM 端口并开始采集。绘图滤波不会覆盖原始记录数据。

## 支持

[LazyingArt 捐助](https://chat.lazying.art/donate) · [PayPal](https://paypal.me/RongzhouChen) · [Stripe](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
