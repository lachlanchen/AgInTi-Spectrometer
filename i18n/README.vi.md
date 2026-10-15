# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner — apps and four buddies](https://lazying.art/media/brand/lazyingart-intro.gif)](https://lazying.art)

![Nguyên mẫu AgInTi Spectrometer](../docs/assets/aginti-spectrometer-hero.png)

AgInTi Spectrometer là bàn làm việc thu nhận và trực quan hóa tốc độ cao cho C12880MA. Một lõi thu nhận dùng chung phục vụ ứng dụng Qt, bảng điều khiển web, ghi CSV, CLI và REST API. Việc đọc nối tiếp được tách khỏi hiển thị để giữ độ phân giải thời gian.

## Tính năng

- Phổ đã hiệu chuẩn trong dải 340–850 nm.
- Phơi sáng cố định, thích nghi hoặc đo một lần từ mức micro giây.
- Tốc độ thu nhận và làm mới giao diện độc lập.
- Trừ ảnh tối, lấy trung bình, lọc, tự động thang đo và CSV thô.
- Giao diện máy tính, web và API cho tự động hóa tác tử.

## Khởi động nhanh

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\spectrum-studio.exe
```

Kết nối thiết bị, chọn cổng COM rồi bắt đầu thu nhận. Bộ lọc hiển thị không thay đổi dữ liệu thô đã ghi.

## Hỗ trợ

<!-- support:start -->
[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/lachlanchen)
[![LazyingArt Support](https://img.shields.io/badge/LazyingArt-Support-0EA5E9?style=for-the-badge)](https://chat.lazying.art/donate)
[![PayPal Support](https://img.shields.io/badge/PayPal-Support-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen)
[![Stripe Support](https://img.shields.io/badge/Stripe-Support-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
<!-- support:end -->
