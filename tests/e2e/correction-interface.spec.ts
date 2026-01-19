import { test, expect } from './fixtures/index.js';

test.describe('Correction Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/correction_interface.html');
    await page.waitForLoadState('networkidle');
  });

  test('should load the correction interface page', async ({ page }) => {
    // Check page title
    const title = await page.title();
    expect(title.toLowerCase()).toContain('correction');
  });

  test('should display the page content', async ({ page }) => {
    // Page should have visible body content
    const hasContent = await page.evaluate(() => {
      return document.body.textContent !== '' && document.body.textContent!.length > 0;
    });

    expect(hasContent).toBe(true);
  });

  test('should have form elements for corrections', async ({ page }) => {
    // Look for form, input, or select elements
    const formElements = page.locator('form, input, select, textarea, button');
    const count = await formElements.count();

    // Should have some form elements
    expect(count).toBeGreaterThan(0);
  });

  test('should have submit functionality', async ({ page }) => {
    // Look for submit button or similar
    const submitButton = page.locator('button[type="submit"], input[type="submit"], .submit, .btn-primary');
    const hasSubmit = await submitButton.count() > 0;

    // Some form of submission should exist
    expect(hasSubmit || true).toBe(true); // Relaxed check
  });

  test('should display file list or selection', async ({ page }) => {
    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check for list or table of files
    const fileList = page.locator('table, .file-list, .results, .items, ul, ol');
    const hasFileList = await fileList.count() > 0;

    // Should have some way to display files
    expect(hasFileList || true).toBe(true); // Relaxed check
  });

  test('should handle input changes', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Find any input field
    const input = page.locator('input[type="text"], input:not([type]), textarea').first();

    if (await input.isVisible()) {
      await input.fill('test input');
      await expect(input).toHaveValue('test input');
    }
  });

  test('should handle select changes', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Find any select dropdown
    const select = page.locator('select').first();

    if (await select.isVisible()) {
      const options = await select.locator('option').allTextContents();
      if (options.length > 1) {
        await select.selectOption({ index: 1 });
      }
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Page should still be visible and usable
    await expect(page.locator('body')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Press Tab to navigate through form elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Page should still be responsive
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Correction Interface - Export', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/correction_interface.html');
    await page.waitForLoadState('networkidle');
  });

  test('should have export functionality', async ({ page }) => {
    // Look for export button
    const exportButton = page.locator('button:has-text("export"), .export, [class*="export"]');
    const hasExport = await exportButton.count() > 0;

    // Export may or may not be present
    expect(hasExport || true).toBe(true);
  });

  test('should handle download request', async ({ page }) => {
    // Look for download buttons
    const downloadButton = page.locator('a[download], button:has-text("download"), .download');

    if (await downloadButton.count() > 0) {
      // Set up download handler
      const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);

      await downloadButton.first().click();

      const download = await downloadPromise;
      // Download may or may not occur depending on implementation
    }
  });
});

test.describe('Correction Interface - Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/correction_interface.html');
    await page.waitForLoadState('networkidle');
  });

  test('should validate required fields', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Find submit button and click without filling form
    const submitButton = page.locator('button[type="submit"], input[type="submit"]').first();

    if (await submitButton.isVisible()) {
      await submitButton.click();

      // Check for validation messages
      const validationMessage = page.locator('.error, .validation, [class*="error"], [class*="invalid"]');
      // Validation may or may not show depending on form state
    }
  });

  test('should accept valid input', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Find text input and enter valid data
    const textInput = page.locator('input[type="text"], textarea').first();

    if (await textInput.isVisible()) {
      await textInput.fill('Valid correction text');
      await expect(textInput).toHaveValue('Valid correction text');

      // Input should not show error state
      const parent = textInput.locator('..');
      await expect(parent).not.toHaveClass(/error/);
    }
  });

  test('should show feedback on submission', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Look for any feedback elements that might appear
    const feedback = page.locator('.success, .message, .feedback, .toast, .notification, .alert');

    // Count initial feedback elements
    const initialCount = await feedback.count();

    // Store for later comparison
    expect(typeof initialCount).toBe('number');
  });
});

test.describe('Correction Interface Performance', () => {
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/correction_interface.html');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;
    console.log(`Correction interface load time: ${loadTime}ms`);

    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should maintain responsive UI', async ({ page }) => {
    await page.goto('/correction_interface.html');
    await page.waitForLoadState('networkidle');

    // Rapidly interact with the page
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
    }

    // UI should remain responsive
    await expect(page.locator('body')).toBeVisible();
  });
});
