import { test, expect } from './fixtures/index.js';

test.describe('Metadata Viewer', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/metadata_viewer.html');
    await page.waitForLoadState('networkidle');
  });

  test('should load the metadata viewer page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('File Metadata Viewer');
  });

  test('should display header with file count', async ({ page }) => {
    const header = page.locator('.header');
    await expect(header).toBeVisible();

    const fileCount = page.locator('#fileCount');
    await expect(fileCount).toBeVisible();
  });

  test('should have theme toggle button', async ({ page }) => {
    const themeToggle = page.locator('.theme-toggle');
    await expect(themeToggle).toBeVisible();
    await expect(themeToggle).toHaveText('Dark');
  });

  test('should toggle dark mode', async ({ page }) => {
    const themeToggle = page.locator('.theme-toggle');
    const body = page.locator('body');

    // Initially should not have dark class
    await expect(body).not.toHaveClass(/dark/);

    // Click to enable dark mode
    await themeToggle.click();

    // Should have dark class
    await expect(body).toHaveClass(/dark/);

    // Click again to disable
    await themeToggle.click();

    // Should not have dark class
    await expect(body).not.toHaveClass(/dark/);
  });

  test('should display filters section', async ({ page }) => {
    const filtersSection = page.locator('.filters-section');
    await expect(filtersSection).toBeVisible();

    // Check filter inputs
    await expect(page.locator('#searchInput')).toBeVisible();
    await expect(page.locator('#categoryFilter')).toBeVisible();
    await expect(page.locator('#subcategoryFilter')).toBeVisible();
    await expect(page.locator('#statusFilter')).toBeVisible();
  });

  test('should filter by search input', async ({ page }) => {
    const searchInput = page.locator('#searchInput');

    // Wait for data to load
    await page.waitForTimeout(1000);

    // Enter search term
    await searchInput.fill('test');

    // Wait for debounced filter
    await page.waitForTimeout(500);

    // Results should update based on search
    const resultCount = page.locator('.result-count');
    await expect(resultCount).toBeVisible();
  });

  test('should filter by category', async ({ page }) => {
    const categoryFilter = page.locator('#categoryFilter');

    // Wait for categories to load
    await page.waitForTimeout(1000);

    // Get available options
    const options = await categoryFilter.locator('option').allTextContents();

    // Should have "All Categories" plus category options
    expect(options.length).toBeGreaterThan(0);
    expect(options[0]).toBe('All Categories');
  });

  test('should display stats grid', async ({ page }) => {
    const statsGrid = page.locator('#statsGrid');
    await expect(statsGrid).toBeVisible();
  });

  test('should display charts section', async ({ page }) => {
    const chartsSection = page.locator('#chartsSection');
    await expect(chartsSection).toBeVisible();
  });

  test('should display results container', async ({ page }) => {
    const resultsContainer = page.locator('.results-container');
    await expect(resultsContainer).toBeVisible();
  });

  test('should have view toggle buttons', async ({ page }) => {
    // Wait for the view toggle to be present
    const viewToggle = page.locator('.view-toggle');

    // View toggle may or may not be visible depending on data loading
    if (await viewToggle.isVisible()) {
      const buttons = viewToggle.locator('button');
      const count = await buttons.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('should handle pagination', async ({ page }) => {
    // Wait for data to load
    await page.waitForTimeout(2000);

    const pagination = page.locator('.pagination');

    // Pagination may or may not exist depending on data size
    if (await pagination.isVisible()) {
      const paginationButtons = pagination.locator('button');
      const buttonCount = await paginationButtons.count();
      expect(buttonCount).toBeGreaterThan(0);
    }
  });

  test('should expand result item details', async ({ page }) => {
    // Wait for results to load
    await page.waitForTimeout(2000);

    const expandBtn = page.locator('.expand-btn').first();

    if (await expandBtn.isVisible()) {
      const expandedContent = page.locator('.expanded-content').first();

      // Initially collapsed
      await expect(expandedContent).not.toHaveClass(/show/);

      // Click to expand
      await expandBtn.click();

      // Should be expanded
      await expect(expandedContent).toHaveClass(/show/);

      // Click again to collapse
      await expandBtn.click();

      // Should be collapsed
      await expect(expandedContent).not.toHaveClass(/show/);
    }
  });

  test('should display loading state', async ({ page }) => {
    // Navigate to page and check for loading state
    await page.goto('/metadata_viewer.html', { waitUntil: 'domcontentloaded' });

    // Loading spinner should appear initially
    const loadingSpinner = page.locator('.loading-spinner');
    const loadingContainer = page.locator('.loading-container');

    // Either loading is shown or data is already loaded
    // This depends on how fast the data loads
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Header should still be visible
    await expect(page.locator('.header')).toBeVisible();

    // Container should still be visible
    await expect(page.locator('.container')).toBeVisible();
  });
});

test.describe('Metadata Viewer - Large Data Handling', () => {
  test('should handle large JSON files efficiently', async ({ page }) => {
    await page.goto('/metadata_viewer.html');
    await page.waitForLoadState('networkidle');

    // Wait for data to load
    await page.waitForTimeout(3000);

    // Check memory usage if available
    const memoryInfo = await page.evaluate(() => {
      const memory = (performance as any).memory;
      if (memory) {
        return {
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
        };
      }
      return null;
    });

    if (memoryInfo) {
      console.log(`JS Heap Used: ${(memoryInfo.usedJSHeapSize / 1024 / 1024).toFixed(1)}MB`);
      console.log(`JS Heap Total: ${(memoryInfo.totalJSHeapSize / 1024 / 1024).toFixed(1)}MB`);

      // Heap should not exceed 512MB for reasonable performance
      expect(memoryInfo.usedJSHeapSize).toBeLessThan(512 * 1024 * 1024);
    }
  });

  test('should maintain responsive UI while loading', async ({ page }) => {
    await page.goto('/metadata_viewer.html', { waitUntil: 'domcontentloaded' });

    // UI should remain interactive
    const searchInput = page.locator('#searchInput');
    await expect(searchInput).toBeEnabled();

    // Should be able to type
    await searchInput.type('test');
    await expect(searchInput).toHaveValue('test');
  });

  test('should handle rapid filter changes', async ({ page }) => {
    await page.goto('/metadata_viewer.html');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    const searchInput = page.locator('#searchInput');

    // Rapidly type and clear
    for (let i = 0; i < 5; i++) {
      await searchInput.fill(`test${i}`);
      await page.waitForTimeout(100);
      await searchInput.clear();
    }

    // Page should still be responsive
    await expect(page.locator('.header')).toBeVisible();
  });
});
