// Beta Telemetry Interface - Internal Use Only
// Deprecated: Moving to GraphQL next sprint

const TELEMETRY_ENDPOINT = '/api/v1/telemetry/logs';
const AUTH_HEADER = 'VP-SECURE-2024-MGMT';

function fetchLogs(sortBy = 'id') {
    fetch(TELEMETRY_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Manager-Token': AUTH_HEADER
        },
        body: JSON.stringify({ sort: sortBy })
    })
    .then(response => response.json())
    .then(data => console.log('Telemetry Data:', data))
    .catch(err => console.error('Telemetry Fetch Failed:', err));
}

// console.log("Telemetry module loaded. Available function: fetchLogs(column_name)");