import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const TELEMETRY_DIR = 'test-results/telemetry';
const METADATA_FILE = 'test-run-metadata.json';

interface TestRunMetadata {
  runId: string;
  correlationId: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  playwright: {
    version: string;
    projects: string[];
  };
  otel: {
    enabled: boolean;
    endpoint: string | null;
  };
  environment: {
    nodeVersion: string;
    platform: string;
    ci: boolean;
  };
}

async function globalTeardown(config: FullConfig): Promise<void> {
  const endTime = new Date();

  // Flush OpenTelemetry spans
  try {
    // Dynamic import to avoid issues if SDK wasn't initialized
    const { sdk } = await import('./global-setup.js');

    if (sdk) {
      await sdk.shutdown();

      if (process.env.OTEL_DEBUG) {
        console.log('[OTEL] SDK shutdown complete, spans flushed');
      }
    }
  } catch (error) {
    // SDK wasn't initialized or shutdown failed
    if (process.env.OTEL_DEBUG) {
      console.log('[OTEL] Shutdown skipped:', error);
    }
  }

  // Update metadata with end time and duration
  const telemetryDir = path.join(process.cwd(), TELEMETRY_DIR);
  const metadataPath = path.join(telemetryDir, METADATA_FILE);

  try {
    if (fs.existsSync(metadataPath)) {
      const metadata: TestRunMetadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));

      metadata.endTime = endTime.toISOString();
      metadata.duration = endTime.getTime() - new Date(metadata.startTime).getTime();

      fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));

      const durationSec = (metadata.duration / 1000).toFixed(2);
      console.log(`\n[E2E Teardown] Test run completed`);
      console.log(`  Duration: ${durationSec}s`);
      console.log(`  Run ID: ${metadata.runId}`);
    }
  } catch (error) {
    console.error('[E2E Teardown] Failed to update metadata:', error);
  }

  // Log HAR files summary
  const harDir = path.join(process.cwd(), 'test-results/har');
  if (fs.existsSync(harDir)) {
    const harFiles = fs.readdirSync(harDir).filter(f => f.endsWith('.har'));
    if (harFiles.length > 0) {
      console.log(`  HAR files: ${harFiles.length} recorded`);
    }
  }

  console.log('');
}

export default globalTeardown;
