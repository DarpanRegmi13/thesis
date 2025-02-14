let isCapturing = false;
let trafficDatabase = []; // Stores all captured traffic
// Mock function to start traffic capture
function startCapture1(targetIp = '') {
    if (isCapturing) return;
    isCapturing = true;

    // Use the target IP if provided, otherwise, the backend will handle using the local IP
    let ipToUse = targetIp || '';

    startCaptureInterval(ipToUse);
}

// Function to start the capture interval
function startCaptureInterval(ip) {

    const trafficData = document.getElementById("traffic-data");
    // Start a capture interval that fetches traffic data every 2 seconds
    const captureInterval = setInterval(() => {
        if (!isCapturing) {
            clearInterval(captureInterval);
            return;
        }

        // Fetch real traffic data from the server, passing the target IP (or empty string for local IP)
        fetch(`http://localhost:5003/api/live-traffic?target_ip=${ip}`) // Adjusted API to accept target IP
            .then(response => response.json())
            .then(traffic => {
                // Push the live traffic data into the database
                trafficDatabase.push(traffic);

                console.log('Captured traffic data:', traffic); // For debug purposes

                // Determine row class based on protocol
                let rowClass = "info";
                if (traffic.protocol === "HTTP") rowClass = "warning";
                if (traffic.protocol === "ICMP") rowClass = "critical";

                // Add traffic to the table
                const row = document.createElement("tr");
                row.className = rowClass;
                row.innerHTML = `
                    <td>${traffic.timestamp}</td>
                    <td>${traffic.srcIP}</td>
                    <td>${traffic.destIP}</td>
                    <td>${traffic.protocol}</td>
                    <td>${traffic.srcPort} → ${traffic.destPort}</td>
                    <td>${traffic.details}</td>
                `;
                trafficData.appendChild(row);

                // Auto-scroll and limit rows
                trafficData.parentNode.scrollTop = trafficData.parentNode.scrollHeight;
                if (trafficData.children.length > 100) {
                    trafficData.removeChild(trafficData.firstChild);
                }
            })
            .catch(error => {
                console.error('Error fetching live traffic data:', error);
            });
    }, 2000);
}

function stopCapture1() {
    isCapturing = false; // Stop the capturing process
    alert("Traffic capture stopped."); // Optional feedback to the user
}

// Save captured data
function saveDatabase1() {
    if (trafficDatabase.length === 0) {
        alert("No data to save!");
        return;
    }

    // Make a POST request to the Flask server to save captured traffic data
    fetch('http://localhost:5003/api/save-traffic', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ trafficData: trafficDatabase }) // Send captured traffic to server
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);  // Show success or failure message
    })
    .catch(error => {
        console.error('Error saving data:', error);
    });
}
