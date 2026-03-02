// VerdantPath Internal Inventory Helper
// Used for automated verification of silo shipments
function checkInventoryItem(id) {
    fetch('/api/v1/inventory/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ item_id: id })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Inventory Status for " + id + ": " + data.status);
    });
}

// Debug: checkInventoryItem('VP-8821');