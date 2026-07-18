# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

![Prototype AgInTi Spectrometer](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer est un poste d’acquisition et de visualisation rapide pour le C12880MA. Un même cœur alimente l’application Qt, le tableau de bord web, l’enregistrement CSV, la CLI et l’API REST. L’acquisition série reste séparée du rendu afin de préserver la résolution temporelle.

## Fonctions

- Spectre étalonné de 340 à 850 nm.
- Exposition fixe, adaptative ou mesurée une fois, dès la microseconde.
- Cadences d’acquisition et d’affichage indépendantes.
- Soustraction du noir, moyennage, filtres, échelle automatique et CSV brut.
- Interfaces bureau, web et automatisation par agents.

## Démarrage

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

Connectez l’instrument, choisissez le port COM et lancez l’acquisition. Les filtres visuels ne modifient jamais les échantillons bruts enregistrés.

## Soutien

[LazyingArt](https://chat.lazying.art/donate) · [PayPal](https://paypal.me/RongzhouChen) · [Stripe](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
