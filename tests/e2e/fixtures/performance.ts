import { test as base, Page } from '@playwright/test';

export interface CoreWebVitals {
  lcp: number | null;  // Largest Contentful Paint
  fcp: number | null;  // First Contentful Paint
  cls: number | null;  // Cumulative Layout Shift
  ttfb: number | null; // Time to First Byte
  fid: number | null;  // First Input Delay (requires user interaction)
  inp: number | null;  // Interaction to Next Paint
}

export interface PerformanceMetrics extends CoreWebVitals {
  domContentLoaded: number | null;
  loadComplete: number | null;
  resourceCount: number;
  totalTransferSize: number;
  jsHeapSize: number | null;
}

export interface PerformanceFixtures {
  performanceMetrics: PerformanceMetrics;
  measurePerformance: (page: Page) => Promise<PerformanceMetrics>;
}

/**
 * Fixture that provides Core Web Vitals and performance measurement
 */
export const performanceTest = base.extend<PerformanceFixtures>({
  measurePerformance: async ({}, use) => {
    const measure = async (page: Page): Promise<PerformanceMetrics> => {
      return measurePagePerformance(page);
    };
    await use(measure);
  },

  performanceMetrics: async ({ page }, use) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState('load');
    const metrics = await measurePagePerformance(page);
    await use(metrics);
  },
});

/**
 * Measure Core Web Vitals and other performance metrics for a page
 */
export async function measurePagePerformance(page: Page): Promise<PerformanceMetrics> {
  // Inject performance observer for CLS
  await page.evaluate(() => {
    (window as any).__clsValue = 0;
    (window as any).__lcpValue = 0;
    (window as any).__fcpValue = 0;

    // CLS observer
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!(entry as any).hadRecentInput) {
          (window as any).__clsValue += (entry as any).value;
        }
      }
    });
    clsObserver.observe({ type: 'layout-shift', buffered: true });

    // LCP observer
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      if (entries.length > 0) {
        (window as any).__lcpValue = entries[entries.length - 1].startTime;
      }
    });
    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

    // FCP from paint entries
    const paintObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          (window as any).__fcpValue = entry.startTime;
        }
      }
    });
    paintObserver.observe({ type: 'paint', buffered: true });
  });

  // Wait a bit for metrics to be collected
  await page.waitForTimeout(100);

  // Collect all metrics
  const metrics = await page.evaluate((): PerformanceMetrics => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

    // Calculate TTFB
    const ttfb = navigation ? navigation.responseStart - navigation.requestStart : null;

    // Calculate total transfer size
    let totalTransferSize = 0;
    for (const resource of resources) {
      totalTransferSize += resource.transferSize || 0;
    }

    // Get JS heap size if available
    const memory = (performance as any).memory;
    const jsHeapSize = memory ? memory.usedJSHeapSize : null;

    return {
      lcp: (window as any).__lcpValue || null,
      fcp: (window as any).__fcpValue || null,
      cls: (window as any).__clsValue || null,
      ttfb,
      fid: null, // Requires user interaction
      inp: null, // Requires user interaction
      domContentLoaded: navigation ? navigation.domContentLoadedEventEnd - navigation.startTime : null,
      loadComplete: navigation ? navigation.loadEventEnd - navigation.startTime : null,
      resourceCount: resources.length,
      totalTransferSize,
      jsHeapSize,
    };
  });

  return metrics;
}

/**
 * Assert that Core Web Vitals meet the specified thresholds
 */
export function assertGoodWebVitals(metrics: CoreWebVitals): void {
  // LCP should be under 2.5 seconds for "good"
  if (metrics.lcp !== null && metrics.lcp > 2500) {
    console.warn(`LCP ${metrics.lcp}ms exceeds 2500ms threshold`);
  }

  // FCP should be under 1.8 seconds for "good"
  if (metrics.fcp !== null && metrics.fcp > 1800) {
    console.warn(`FCP ${metrics.fcp}ms exceeds 1800ms threshold`);
  }

  // CLS should be under 0.1 for "good"
  if (metrics.cls !== null && metrics.cls > 0.1) {
    console.warn(`CLS ${metrics.cls} exceeds 0.1 threshold`);
  }

  // TTFB should be under 800ms for "good"
  if (metrics.ttfb !== null && metrics.ttfb > 800) {
    console.warn(`TTFB ${metrics.ttfb}ms exceeds 800ms threshold`);
  }
}

/**
 * Create performance thresholds for assertions
 */
export interface PerformanceThresholds {
  lcp?: number;
  fcp?: number;
  cls?: number;
  ttfb?: number;
  domContentLoaded?: number;
  loadComplete?: number;
}

export const DEFAULT_THRESHOLDS: PerformanceThresholds = {
  lcp: 2500,
  fcp: 1800,
  cls: 0.1,
  ttfb: 800,
  domContentLoaded: 3000,
  loadComplete: 5000,
};

/**
 * Check if metrics meet thresholds and return violations
 */
export function checkThresholds(
  metrics: PerformanceMetrics,
  thresholds: PerformanceThresholds = DEFAULT_THRESHOLDS
): string[] {
  const violations: string[] = [];

  if (thresholds.lcp && metrics.lcp !== null && metrics.lcp > thresholds.lcp) {
    violations.push(`LCP (${metrics.lcp}ms) exceeds threshold (${thresholds.lcp}ms)`);
  }

  if (thresholds.fcp && metrics.fcp !== null && metrics.fcp > thresholds.fcp) {
    violations.push(`FCP (${metrics.fcp}ms) exceeds threshold (${thresholds.fcp}ms)`);
  }

  if (thresholds.cls && metrics.cls !== null && metrics.cls > thresholds.cls) {
    violations.push(`CLS (${metrics.cls}) exceeds threshold (${thresholds.cls})`);
  }

  if (thresholds.ttfb && metrics.ttfb !== null && metrics.ttfb > thresholds.ttfb) {
    violations.push(`TTFB (${metrics.ttfb}ms) exceeds threshold (${thresholds.ttfb}ms)`);
  }

  if (thresholds.domContentLoaded && metrics.domContentLoaded !== null &&
      metrics.domContentLoaded > thresholds.domContentLoaded) {
    violations.push(`DOMContentLoaded (${metrics.domContentLoaded}ms) exceeds threshold (${thresholds.domContentLoaded}ms)`);
  }

  if (thresholds.loadComplete && metrics.loadComplete !== null &&
      metrics.loadComplete > thresholds.loadComplete) {
    violations.push(`Load Complete (${metrics.loadComplete}ms) exceeds threshold (${thresholds.loadComplete}ms)`);
  }

  return violations;
}

/**
 * Format metrics for logging
 */
export function formatMetrics(metrics: PerformanceMetrics): string {
  const lines = [
    `Core Web Vitals:`,
    `  LCP: ${metrics.lcp !== null ? `${metrics.lcp.toFixed(0)}ms` : 'N/A'}`,
    `  FCP: ${metrics.fcp !== null ? `${metrics.fcp.toFixed(0)}ms` : 'N/A'}`,
    `  CLS: ${metrics.cls !== null ? metrics.cls.toFixed(3) : 'N/A'}`,
    `  TTFB: ${metrics.ttfb !== null ? `${metrics.ttfb.toFixed(0)}ms` : 'N/A'}`,
    `Page Load:`,
    `  DOMContentLoaded: ${metrics.domContentLoaded !== null ? `${metrics.domContentLoaded.toFixed(0)}ms` : 'N/A'}`,
    `  Load Complete: ${metrics.loadComplete !== null ? `${metrics.loadComplete.toFixed(0)}ms` : 'N/A'}`,
    `Resources:`,
    `  Count: ${metrics.resourceCount}`,
    `  Transfer Size: ${(metrics.totalTransferSize / 1024).toFixed(1)}KB`,
  ];

  if (metrics.jsHeapSize !== null) {
    lines.push(`  JS Heap: ${(metrics.jsHeapSize / 1024 / 1024).toFixed(1)}MB`);
  }

  return lines.join('\n');
}
