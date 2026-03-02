// Aegis-Track Legacy Telemetry Fetcher
// This script handles historical data retrieval for the dashboard
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const shipmentId = window.location.pathname.split('/').pop();
    
    if (shipmentId && !isNaN(shipmentId)) {
        console.log("Initializing archive telemetry fetch for shipment: " + shipmentId);
        // We keep the old archive endpoint for backward compatibility with 2021 sensors
        fetch(`/api/v1/telemetry/archive?shipment_id=${shipmentId}&sensor_type=temp`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log("Archive data successfully synchronized.");
                }
            });
    }
});