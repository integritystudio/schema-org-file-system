import { test as base, BrowserContext } from '@playwright/test';
import path from 'path';
import fs from 'fs';

export interface HarRecordingOptions {
  harPath: string;
  recordHar: boolean;
}

export interface HarRecordingFixtures {
  harRecording: HarRecordingOptions;
  harContext: BrowserContext;
}

const HAR_OUTPUT_DIR = 'test-results/har';

/**
 * Fixture that enables HAR recording for each test.
 * HAR files are saved to test-results/har/<test-file>-<test-title>.har
 */
export const harRecordingTest = base.extend<HarRecordingFixtures>({
  harRecording: async ({}, use, testInfo) => {
    // Sanitize test name for filename
    const sanitizedTitle = testInfo.title
      .replace(/[^a-zA-Z0-9-_]/g, '-')
      .replace(/-+/g, '-')
      .toLowerCase();

    const testFile = testInfo.file.split('/').pop()?.replace('.spec.ts', '') || 'unknown';
    const harFileName = `${testFile}-${sanitizedTitle}.har`;
    const harPath = path.join(process.cwd(), HAR_OUTPUT_DIR, harFileName);

    // Ensure HAR directory exists
    const harDir = path.dirname(harPath);
    if (!fs.existsSync(harDir)) {
      fs.mkdirSync(harDir, { recursive: true });
    }

    await use({
      harPath,
      recordHar: true,
    });
  },

  harContext: async ({ browser, harRecording }, use) => {
    // Create a new context with HAR recording enabled
    const context = await browser.newContext({
      recordHar: {
        path: harRecording.harPath,
        mode: 'full',
        content: 'embed',
      },
    });

    await use(context);

    // Close context to finalize HAR file
    await context.close();
  },
});

/**
 * Start HAR recording for an existing context
 * Note: This is a workaround since Playwright doesn't support starting HAR recording
 * on an existing context. Consider creating a new context with HAR enabled instead.
 */
export function getHarPath(testName: string, testFile: string): string {
  const sanitizedTitle = testName
    .replace(/[^a-zA-Z0-9-_]/g, '-')
    .replace(/-+/g, '-')
    .toLowerCase();

  const file = testFile.split('/').pop()?.replace('.spec.ts', '') || 'unknown';
  const harFileName = `${file}-${sanitizedTitle}.har`;

  return path.join(process.cwd(), HAR_OUTPUT_DIR, harFileName);
}

/**
 * Create a browser context with HAR recording enabled
 */
export async function createHarContext(
  browser: import('@playwright/test').Browser,
  testName: string,
  testFile: string
): Promise<BrowserContext> {
  const harPath = getHarPath(testName, testFile);

  // Ensure directory exists
  const harDir = path.dirname(harPath);
  if (!fs.existsSync(harDir)) {
    fs.mkdirSync(harDir, { recursive: true });
  }

  return browser.newContext({
    recordHar: {
      path: harPath,
      mode: 'full',
      content: 'embed',
    },
  });
}

/**
 * Analyze HAR file and return summary statistics
 */
export interface HarSummary {
  totalRequests: number;
  totalSize: number;
  avgResponseTime: number;
  slowestRequest: {
    url: string;
    time: number;
  } | null;
  requestsByType: Record<string, number>;
  errors: Array<{ url: string; status: number }>;
}

export async function analyzeHar(harPath: string): Promise<HarSummary | null> {
  try {
    const harContent = fs.readFileSync(harPath, 'utf-8');
    const har = JSON.parse(harContent);
    const entries = har.log?.entries || [];

    let totalSize = 0;
    let totalTime = 0;
    let slowestRequest: { url: string; time: number } | null = null;
    const requestsByType: Record<string, number> = {};
    const errors: Array<{ url: string; status: number }> = [];

    for (const entry of entries) {
      const time = entry.time || 0;
      const size = entry.response?.content?.size || 0;
      const status = entry.response?.status || 0;
      const url = entry.request?.url || '';
      const mimeType = entry.response?.content?.mimeType || 'unknown';

      totalSize += size;
      totalTime += time;

      // Track by MIME type
      const type = mimeType.split('/')[0] || 'unknown';
      requestsByType[type] = (requestsByType[type] || 0) + 1;

      // Track slowest request
      if (!slowestRequest || time > slowestRequest.time) {
        slowestRequest = { url, time };
      }

      // Track errors
      if (status >= 400) {
        errors.push({ url, status });
      }
    }

    return {
      totalRequests: entries.length,
      totalSize,
      avgResponseTime: entries.length > 0 ? totalTime / entries.length : 0,
      slowestRequest,
      requestsByType,
      errors,
    };
  } catch (error) {
    console.error(`Failed to analyze HAR file: ${harPath}`, error);
    return null;
  }
}
