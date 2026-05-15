# Phase 5 Plan — Operator & Security Hardening

Date: 2026-05-15
Owner: Founders + engineering
Status: In progress

## Goal

Operator dashboard dan internal API aman dipakai lebih dari 1 founder/operator, tanpa shared token yang disimpan di browser.

## Baseline Findings

- `frontend/src/app/operator/page.tsx` sebelumnya memakai `localStorage` key `smartdesign_operator_token`.
- `backend/app/api/internal_metrics.py` sebelumnya mengandalkan `X-Internal-Token`.
- Model user belum memiliki `role`.
- `quantum-engine/README.md` masih berpotensi dibaca sebagai service aktif jika dibaca sekilas.

## Scope

| Area | Target |
| --- | --- |
| Operator auth | Ganti localStorage shared token dengan session login + admin role |
| Internal API | `/api/internal/*` wajib admin identity, bukan shared token |
| Frontend operator | `/operator` pakai NextAuth session dan bearer token |
| Asset security | Putuskan policy public/signed URL, retention, malware scan |
| Legacy cleanup | `quantum-engine` jelas ditandai archived/deprecated |
| Docs/UAT | Launch readiness + runbook diperbarui |

## Technical Decisions

1. Admin bootstrap
- Tambah kolom `users.role` dengan default `user`.
- Admin dianggap valid jika:
  - `users.role == "admin"`, atau
  - email ada di `OPERATOR_ADMIN_EMAILS` (fallback bootstrap founder/operator awal).

2. Internal API guard
- Internal endpoints wajib identity-based auth.
- `ALLOW_INTERNAL_TOKEN_FALLBACK=false` sebagai default.
- Jika fallback diaktifkan (`true`), token lama hanya sebagai transisi operasional.

3. Frontend operator auth
- Hilangkan input token manual dan localStorage persistence.
- Gunakan `useSession()` + `Authorization: Bearer <session.accessToken>`.
- Role check via backend profile (`/api/users/me`) sebelum render dashboard data.

## Execution Order

1. Admin role model + migration + schema/auth response.
2. Protect internal endpoints dengan admin guard.
3. Refactor `/operator` ke session auth.
4. Verifikasi tests + lint/build.
5. Asset/security policy documentation.
6. Legacy tombstone + launch closeout docs.

## Acceptance Criteria

- Unauthenticated -> 401 pada endpoint internal.
- Authenticated non-admin -> 403.
- Authenticated admin -> 200.
- Tidak ada shared internal token tersimpan di browser.
- Policy signed URL + malware scanning terdokumentasi dengan owner dan target schedule.
- Legacy `quantum-engine` tidak ambigu sebagai runtime aktif.
