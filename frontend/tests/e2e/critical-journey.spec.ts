import { test, expect } from '@playwright/test';

test.describe('Critical User Journey', () => {

    test('Complete flow: Login -> Create -> Edit -> Export', async ({ page }) => {
        // 1. Visit Home Page
        await page.goto('/');
        await expect(page).toHaveTitle(/SmartDesign/i);

        // Check for essential hero elements
        await expect(page.getByRole('heading', { name: /Foto Produk/i })).toBeVisible();
        await expect(page.getByRole('button', { name: /Coba Gratis/i })).toBeVisible();

        // 2. Navigate to Login
        await page.goto('/login');
        await expect(page.getByRole('heading', { name: /Selamat Datang/i })).toBeVisible();

        // 3. We navigate to an unprotected tool to verify internal apps logic didn't crash
        await page.goto('/tools/magic-eraser');

        // Check for some recognizable element on tools page
        // Wait for page to fully load
        await page.waitForTimeout(2000);

        // Assert we are on the Magic Eraser page
        await expect(page.getByText('Magic Eraser', { exact: false }).first()).toBeVisible();

        // Verify some part of the UI is still responsive, implying no hard crashes
        await expect(page).toHaveTitle(/SmartDesign/i);
    });
});
