# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

![Prototipo de AgInTi Spectrometer](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer es un banco de adquisición y visualización de alta velocidad para el C12880MA. Un único núcleo alimenta la aplicación Qt, el panel web, el registro CSV, la CLI y la API REST. La adquisición serie permanece separada del renderizado para conservar la resolución temporal.

## Funciones

- Espectro calibrado de 340–850 nm.
- Exposición fija, adaptativa o medida una vez, desde microsegundos.
- Tasas independientes de adquisición y actualización visual.
- Sustracción de oscuro, promediado, filtros, autoescala y CSV sin procesar.
- Interfaces de escritorio, web y automatización por agentes.

## Inicio rápido

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

Conecte el instrumento, seleccione el puerto COM e inicie la adquisición. Los filtros visuales no modifican los datos brutos guardados.

## Apoyo

[LazyingArt](https://chat.lazying.art/donate) · [PayPal](https://paypal.me/RongzhouChen) · [Stripe](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
