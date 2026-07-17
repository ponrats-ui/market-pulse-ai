# Notification Channels

Phase E defines provider interfaces only. No provider sends real messages.

## Prepared Channels

- Email
- LINE Messaging API
- Telegram Bot
- Web Push

## Safety Requirements

- No credentials are committed.
- No test sends an outbound message.
- Provider responses clearly report `provider_unavailable`.
- Generated notifications show `sent: false`.
- Delivery failures are captured in alert audit records.

## Future Setup

Future production work can connect real providers behind the existing interfaces after adding secrets management, opt-in consent, unsubscribe controls, retry limits, and abuse prevention.

## Thai Summary

Phase E เตรียม interface สำหรับช่องทางแจ้งเตือนเท่านั้น ยังไม่ส่งข้อความจริงและไม่เก็บ secret ใด ๆ ใน Git.
