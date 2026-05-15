# Phase 5 Asset Access & Retention Policy

Date: 2026-05-15
Status: Approved for controlled beta
Owner: Engineering + founders

## Scope

Dokumen ini menetapkan keputusan keamanan aset untuk controlled paid beta, termasuk akses URL, retensi, dan keputusan malware scanning.

## Asset Classification

1. User uploads
- Foto produk, mask, brand docs, dan file input user lain.

2. Generated assets
- Output AI dan hasil render/export yang disimpan untuk pengguna.

3. Temporary provider assets
- File sementara untuk request provider, intermediate artifacts, dan cache sementara.

4. Brand kit assets
- Logo, guideline PDF, dan metadata branding.

## Current State

- Storage service saat ini masih mengembalikan public URL untuk sebagian besar aset.
- Validation upload untuk image/PDF sudah ada (size + signature checks), tetapi belum ada malware scanning pipeline.

## Decision for Controlled Beta

1. URL access policy
- Public URL masih dianggap acceptable untuk controlled beta kecil (30-50 seller) dengan monitoring.
- Signed/private URL wajib sebelum open beta/public launch.

2. Retention policy
- Temporary provider/source uploads:
  - target cleanup 7-30 hari (tergantung tipe workload).
- User project assets:
  - retain sampai user menghapus project/account.
- Deleted account/project:
  - best-effort storage deletion + quota reconcile.

3. Malware scanning policy
- Deferred untuk controlled beta.
- Wajib dievaluasi dan diputuskan sebelum:
  - traffic publik skala besar,
  - kebutuhan enterprise/compliance,
  - dukungan file non-image lebih luas.

## Risk Ownership & Timeline

- Owner: backend lead + founder ops.
- By next launch gate (open beta readiness):
  - putuskan signed URL rollout plan,
  - putuskan malware scanning approach (inline vs async scan),
  - validasi retention automation cron/worker.

## Exit Criteria Before Open Beta

- Operator endpoints sudah role-protected (no shared browser token).
- Signed/private URL rollout plan committed.
- Retention cleanup berjalan otomatis dengan monitoring.
- Malware scanning decision tercatat sebagai implement/defer dengan alasan bisnis dan risiko.
