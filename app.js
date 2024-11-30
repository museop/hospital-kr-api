// Initialize the map
const map = L.map('map').setView([37.5665, 126.9780], 13); // Default to Seoul, South Korea

let markers = []; // Array to store map markers

// Add tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '© OpenStreetMap'
}).addTo(map);

const resultsDiv = document.getElementById('results');

// Function to clear results
function clearResults() {
  resultsDiv.innerHTML = '';
}

function clearMarkers() {
  markers.forEach(marker => marker.remove()); // Remove each marker from the map
  markers = []; // Clear the markers array
}

// Function to display results
function displayResults(data) {
  clearResults();
  clearMarkers();

  if (!data || data.length === 0) {
    resultsDiv.innerHTML = '<p>No places found.</p>';
    return;
  }

  // Add markers to the map
  data.forEach(place => {
    // Parse location if it's a string
    const location = typeof place.location === 'string' ? JSON.parse(place.location) : place.location;

    if (!location || !location.coordinates) {
      console.warn(`Missing location for place: ${place.name}`);
      return;
    }

    const [longitude, latitude] = location.coordinates;

    const marker = L.marker([latitude, longitude]).addTo(map);
    marker.bindPopup(`<b>${place.name}</b><br>${place.address || ''}`);

    // Add marker to the markers array
    markers.push(marker);

    // Add to results list
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';
    resultItem.innerHTML = `
      <h3>${place.name}</h3>
      <p><b>Address:</b> ${place.address || 'N/A'}</p>
      <p><b>Department:</b> ${place.department_content || 'N/A'}</p>
    `;

    // Add click event to center the map on this place
    resultItem.addEventListener('click', () => {
      map.setView([latitude, longitude], 15); // Zoom level 15 for better focus
      marker.openPopup(); // Open the popup on the marker
    });

    resultsDiv.appendChild(resultItem);
  });
}

// Function 1: Search by Keyword
document.getElementById('searchKeyword').addEventListener('click', async () => {
  const keyword = document.getElementById('keyword').value.trim();
  const maxResults = document.getElementById('maxResults').value || 30;

  if (!keyword) {
    alert('Please enter a keyword');
    return;
  }

  const response = await fetch(`http://127.0.0.1:5000/search_by_keyword?keyword=${encodeURIComponent(keyword)}&max_results=${maxResults}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  const json = await response.json();
  console.log(json);
  if (json.status === 'success') {
    displayResults(json.data);
  } else {
    alert('Error fetching data: ' + json.message);
  }
});

// Function 2: Search Nearby
document.getElementById('searchLocation').addEventListener('click', async () => {
  const bounds = map.getBounds();
  const center = bounds.getCenter();
  const radius = Math.min(bounds.getNorthEast().distanceTo(bounds.getSouthWest()) / 2, 5000); // Max 5km
  const maxResults = document.getElementById('maxResults').value || 30;
  const keyword = document.getElementById('keyword').value.trim();

  // Display the radius information
  document.getElementById('radiusInfo').innerText = `Search Radius: ${Math.round(radius)} meters`;

  const response = await fetch(`http://127.0.0.1:5000/search_hospitals?latitude=${center.lat}&longitude=${center.lng}&radius=${radius}&max_results=${maxResults}&keyword=${encodeURIComponent(keyword)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  });
  const json = await response.json();
  if (json.status === 'success') {
    displayResults(json.data);
  } else {
    alert('Error fetching data: ' + json.message);
  }
});
