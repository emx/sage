import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const BASE_URL = __ENV.SAGE_API_URL || 'http://localhost:8080';
const queryDuration = new Trend('query_duration');

export const options = {
    scenarios: {
        memory_query: {
            executor: 'constant-vus',
            vus: 10,
            duration: '1m',
        },
    },
    thresholds: {
        http_req_duration: ['p(95)<200'],
        http_req_failed: ['rate<0.01'],
    },
};

function randomEmbedding(dims) {
    const emb = [];
    for (let i = 0; i < dims; i++) {
        emb.push(Math.random() * 2 - 1);
    }
    return emb;
}

export default function () {
    const payload = JSON.stringify({
        embedding: randomEmbedding(1536),
        domain_tag: 'crypto',
        top_k: 10,
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
            'X-Agent-ID': 'benchmark-query-' + __VU,
            'X-Signature': 'benchmark-sig',
            'X-Timestamp': Math.floor(Date.now() / 1000).toString(),
        },
        tags: { name: 'memory_query' },
    };

    const start = Date.now();
    const res = http.post(`${BASE_URL}/v1/memory/query`, payload, params);
    queryDuration.add(Date.now() - start);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'has results': (r) => r.json('results') !== undefined,
    });

    sleep(0.5);
}
