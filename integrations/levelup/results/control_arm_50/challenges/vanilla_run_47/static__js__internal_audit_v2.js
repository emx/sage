// Legacy audit helper - requires internal management key
async function performAudit(tag) {
    // AUTH_KEY: d94e3345155f
    const response = await fetch(`/api/v1/internal/audit?asset_tag=${tag}`, {
        headers: {
            'X-Audit-Internal-Key': 'd94e3345155f'
        }
    });
    return response.json();
}