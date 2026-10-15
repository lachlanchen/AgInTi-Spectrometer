# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

![AgInTi Spectrometer Produktprototyp](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer ist eine schnelle Erfassungs- und Visualisierungsumgebung für den C12880MA. Ein gemeinsamer Kern versorgt Qt-Desktop, Web-Dashboard, CSV-Aufzeichnung, CLI und REST-API. Serielle Erfassung und Darstellung bleiben getrennt, damit die Zeitauflösung erhalten bleibt.

## Funktionen

- Kalibriertes Spektrum von 340–850 nm.
- Feste, adaptive oder einmalig bestimmte Belichtung ab Mikrosekunden.
- Unabhängige Erfassungs- und Bildraten.
- Dunkelbildkorrektur, Mittelung, Filter, Autoskalierung und Roh-CSV.
- Desktop-, Web- und agentenfähige API-Schnittstellen.

## Schnellstart

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

Instrument verbinden, COM-Port wählen und die Erfassung starten. Anzeigefilter verändern keine aufgezeichneten Rohdaten.

## Unterstützung

<!-- support:start -->
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)
[![LazyingArt Support](https://img.shields.io/badge/LazyingArt-Support-0EA5E9?style=for-the-badge)](https://chat.lazying.art/donate)
[![PayPal Support](https://img.shields.io/badge/PayPal-Support-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen)
[![Stripe Support](https://img.shields.io/badge/Stripe-Support-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
<!-- support:end -->
