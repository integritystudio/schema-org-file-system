import { test as base, mergeTests } from '@playwright/test';
import { trafficTrackingTest, TrafficTrackingFixtures } from './traffic-tracking.js';
import { harRecordingTest, HarRecordingFixtures } from './har-recording.js';
import { otelTracingTest, OtelTracingFixtures } from './otel-tracing.js';
import { performanceTest, PerformanceFixtures } from './performance.js';

// Re-export individual fixtures for selective use
export { trafficTrackingTest, type TrafficTrackingFixtures } from './traffic-tracking.js';
export { harRecordingTest, type HarRecordingFixtures, analyzeHar, type HarSummary } from './har-recording.js';
export { otelTracingTest, type OtelTracingFixtures, createTestSpan, withSpan, addSpanEvent } from './otel-tracing.js';
export {
  performanceTest,
  type PerformanceFixtures,
  type CoreWebVitals,
  type PerformanceMetrics,
  measurePagePerformance,
  assertGoodWebVitals,
  checkThresholds,
  formatMetrics,
  DEFAULT_THRESHOLDS,
  type PerformanceThresholds,
} from './performance.js';

// Combined fixtures type
export type AllFixtures = TrafficTrackingFixtures & HarRecordingFixtures & OtelTracingFixtures & PerformanceFixtures;

/**
 * Merged test with all fixtures available:
 * - trafficTracking: Inject tracking headers
 * - trackedPage: Page with tracking headers on all requests
 * - harRecording: HAR recording options
 * - harContext: Context with HAR recording enabled
 * - otelTracing: OpenTelemetry tracer and test span
 * - tracedPage: Page with OTEL spans for network requests
 * - measurePerformance: Function to measure page performance
 * - performanceMetrics: Automatically collected performance metrics
 */
export const test = mergeTests(
  trafficTrackingTest,
  harRecordingTest,
  otelTracingTest,
  performanceTest
);

// Re-export expect for convenience
export { expect } from '@playwright/test';

// Export a simple base test for tests that don't need all fixtures
export { base as baseTest };
