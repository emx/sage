import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import crypto from 'k6/crypto';

const BASE_URL = __ENV.SAGE_API_URL || 'http://localhost:8080';

// Custom metrics
const submitErrors = new Rate('submit_errors');
const submitDuration = new Trend('submit_duration');

export const options = {
    scenarios: {
        memory_submit: {
            executor: 'constant-arrival-rate',
            rate: 50,
            timeUnit: '1s',
            duration: '2m',
            preAllocatedVUs: 20,
            maxVUs: 100,
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<500'],
        http_req_failed: ['rate<0.01'],
        submit_errors: ['rate<0.05'],
    },
};

const domains = ['crypto', 'vuln_intel', 'challenge_generation', 'solver_feedback', 'calibration'];
const memTypes = ['fact', 'observation', 'inference'];

export default function () {
    const domain = domains[Math.floor(Math.random() * domains.length)];
    const memType = memTypes[Math.floor(Math.random() * memTypes.length)];
    const content = `Benchmark memory ${Date.now()} - ${crypto.randomBytes(16)}`;

    const payload = JSON.stringify({
        content: content,
        memory_type: memType,
        domain_tag: domain,
        confidence_score: Math.random() * 0.5 + 0.5,
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
            'X-Agent-ID': 'benchmark-agent-' + __VU,
            'X-Signature': 'benchmark-sig',
            'X-Timestamp': Math.floor(Date.now() / 1000).toString(),
        },
        tags: { name: 'memory_submit' },
    };

    const start = Date.now();
    const res = http.post(`${BASE_URL}/v1/memory/submit`, payload, params);
    submitDuration.add(Date.now() - start);

    const success = check(res, {
        'status is 201': (r) => r.status === 201,
        'has memory_id': (r) => r.json('memory_id') !== undefined,
    });

    submitErrors.add(!success);
    sleep(0.1);
}
