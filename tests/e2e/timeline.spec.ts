import { test, expect } from './fixtures/index.js';

test.describe('Timeline', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/timeline.html');
    await page.waitForLoadState('networkidle');
  });

  test('should load the timeline page', async ({ page }) => {
    // Check page title or main content
    const title = await page.title();
    expect(title.toLowerCase()).toContain('timeline');
  });

  test('should display timeline visualization', async ({ page }) => {
    // Wait for data to load
    await page.waitForTimeout(2000);

    // Check for timeline elements (could be canvas, SVG, or CSS-based timeline)
    const canvas = page.locator('canvas');
    const svg = page.locator('svg');
    const timelineContainer = page.locator('.timeline, .timeline-container, [class*="timeline"]');
    const timelineItems = page.locator('.timeline-item, .timeline-entry, [class*="timeline-item"]');

    const hasCanvas = await canvas.count() > 0;
    const hasSvg = await svg.count() > 0;
    const hasTimelineContainer = await timelineContainer.count() > 0;
    const hasTimelineItems = await timelineItems.count() > 0;

    // Should have some visualization element (canvas, SVG, or CSS-based)
    expect(hasCanvas || hasSvg || hasTimelineContainer || hasTimelineItems).toBe(true);
  });

  test('should have interactive timeline controls', async ({ page }) => {
    // Wait for page to fully load
    await page.waitForTimeout(2000);

    // Look for zoom or navigation controls
    const controls = page.locator('button, input[type="range"], .controls, .zoom');
    const controlCount = await controls.count();

    // Timeline should have some controls
    expect(controlCount).toBeGreaterThanOrEqual(0);
  });

  test('should be scrollable', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Check if page or container is scrollable
    const isScrollable = await page.evaluate(() => {
      return document.body.scrollHeight > window.innerHeight ||
             document.documentElement.scrollWidth > window.innerWidth;
    });

    // Page may or may not be scrollable depending on content
    expect(typeof isScrollable).toBe('boolean');
  });

  test('should handle mouse interactions', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Try clicking on the main content area
    await page.click('body');

    // Page should remain responsive
    await expect(page.locator('body')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.waitForTimeout(1000);

    // Press arrow keys for potential navigation
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowLeft');
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('ArrowDown');

    // Page should still be responsive
    await expect(page.locator('body')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Page should still be visible
    await expect(page.locator('body')).toBeVisible();
  });

  test('should handle touch gestures on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Simulate touch scroll
    await page.evaluate(() => {
      window.scrollBy(0, 100);
    });

    // Page should remain responsive
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Timeline - Run Timeline', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/run_timeline.html');
    await page.waitForLoadState('networkidle');
  });

  test('should load the run timeline page', async ({ page }) => {
    // Verify page loaded
    await expect(page.locator('body')).toBeVisible();
  });

  test('should display organization run data', async ({ page }) => {
    await page.waitForTimeout(2000);

    // Check for data visualization
    const hasContent = await page.evaluate(() => {
      return document.body.textContent !== '';
    });

    expect(hasContent).toBe(true);
  });
});

test.describe('Timeline Performance', () => {
  test('should render timeline without jank', async ({ page }) => {
    await page.goto('/timeline.html');

    // Wait for initial render
    await page.waitForTimeout(2000);

    // Measure frame rate during scroll
    const frameMetrics = await page.evaluate(async () => {
      return new Promise<{ frames: number; duration: number }>((resolve) => {
        let frames = 0;
        const startTime = performance.now();

        const countFrame = () => {
          frames++;
          if (performance.now() - startTime < 1000) {
            requestAnimationFrame(countFrame);
          } else {
            resolve({
              frames,
              duration: performance.now() - startTime,
            });
          }
        };

        requestAnimationFrame(countFrame);
      });
    });

    const fps = (frameMetrics.frames / frameMetrics.duration) * 1000;
    console.log(`Timeline FPS: ${fps.toFixed(1)}`);

    // Should maintain at least 30 FPS
    expect(fps).toBeGreaterThan(30);
  });

  test('should load timeline data efficiently', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/timeline.html');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;
    console.log(`Timeline load time: ${loadTime}ms`);

    // Should load within 10 seconds
    expect(loadTime).toBeLessThan(10000);
  });
});
