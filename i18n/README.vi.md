# AgInTi Spectrometer

[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

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

[LazyingArt](https://chat.lazying.art/donate) · [PayPal](https://paypal.me/RongzhouChen) · [Stripe](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400)
