import { test as base, Page, BrowserContext } from '@playwright/test';
import { v4 as uuidv4 } from 'uuid';

export interface TrafficTrackingOptions {
  correlationId: string;
  testName: string;
  testFile: string;
}

export interface TrafficTrackingFixtures {
  trafficTracking: TrafficTrackingOptions;
  trackedPage: Page;
}

/**
 * Fixture that injects traffic tracking headers on all requests.
 * Headers added:
 * - X-Test-Traffic: playwright-e2e
 * - X-Request-ID: <uuid-per-request>
 * - X-Correlation-ID: <uuid-per-test-run>
 * - X-Test-Name: <test-title>
 * - X-Test-File: <spec-filename>
 */
export const trafficTrackingTest = base.extend<TrafficTrackingFixtures>({
  trafficTracking: async ({}, use, testInfo) => {
    const correlationId = process.env.TEST_CORRELATION_ID || uuidv4();
    const testName = testInfo.title;
    const testFile = testInfo.file.split('/').pop() || 'unknown';

    await use({
      correlationId,
      testName,
      testFile,
    });
  },

  trackedPage: async ({ page, trafficTracking }, use) => {
    // Intercept all requests and add tracking headers
    await page.route('**/*', async (route) => {
      const requestId = uuidv4();
      const headers = {
        ...route.request().headers(),
        'X-Test-Traffic': 'playwright-e2e',
        'X-Request-ID': requestId,
        'X-Correlation-ID': trafficTracking.correlationId,
        'X-Test-Name': trafficTracking.testName,
        'X-Test-File': trafficTracking.testFile,
      };

      await route.continue({ headers });
    });

    await use(page);
  },
});

/**
 * Setup traffic tracking for an existing page without using fixtures
 */
export async function setupTrafficTracking(
  page: Page,
  options: Partial<TrafficTrackingOptions> = {}
): Promise<void> {
  const correlationId = options.correlationId || process.env.TEST_CORRELATION_ID || uuidv4();
  const testName = options.testName || 'unknown';
  const testFile = options.testFile || 'unknown';

  await page.route('**/*', async (route) => {
    const requestId = uuidv4();
    const headers = {
      ...route.request().headers(),
      'X-Test-Traffic': 'playwright-e2e',
      'X-Request-ID': requestId,
      'X-Correlation-ID': correlationId,
      'X-Test-Name': testName,
      'X-Test-File': testFile,
    };

    await route.continue({ headers });
  });
}

/**
 * Setup traffic tracking for an entire browser context
 */
export async function setupContextTrafficTracking(
  context: BrowserContext,
  options: Partial<TrafficTrackingOptions> = {}
): Promise<void> {
  const correlationId = options.correlationId || process.env.TEST_CORRELATION_ID || uuidv4();
  const testName = options.testName || 'unknown';
  const testFile = options.testFile || 'unknown';

  await context.route('**/*', async (route) => {
    const requestId = uuidv4();
    const headers = {
      ...route.request().headers(),
      'X-Test-Traffic': 'playwright-e2e',
      'X-Request-ID': requestId,
      'X-Correlation-ID': correlationId,
      'X-Test-Name': testName,
      'X-Test-File': testFile,
    };

    await route.continue({ headers });
  });
}
