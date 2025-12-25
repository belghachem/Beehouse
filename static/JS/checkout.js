// Shipping rates data
const shippingRates = {
    'Mostaganem': { home: 600, stop: 400 },
    'Mascara': { home: 750, stop: 450 },
    'Saida': { home: 750, stop: 450 },
    'Oran': { home: 750, stop: 450 },
    'Alger': { home: 700, stop: 450 },
    'Boumerdès': { home: 800, stop: 500 },
    'Blida': { home: 800, stop: 500 },
    'Tipaza': { home: 800, stop: 500 },
    'Tizi Ouzou': { home: 800, stop: 500 },
    'Bouira': { home: 800, stop: 500 },
    'Béjaïa': { home: 800, stop: 500 },
    'Médéa': { home: 800, stop: 500 },
    'Aïn Defla': { home: 800, stop: 500 },
    'Aïn Témouchent': { home: 800, stop: 500 },
    'Chlef': { home: 800, stop: 500 },
    'Constantine': { home: 800, stop: 500 },
    'Sétif': { home: 800, stop: 500 },
    'Tiaret': { home: 800, stop: 500 },
    'Tlemcen': { home: 800, stop: 500 },
    'Relizane': { home: 800, stop: 500 },
    'Sidi Bel Abbès': { home: 800, stop: 500 },
    'Jijel': { home: 900, stop: 600 },
    'Bordj Bou Arréridj': { home: 900, stop: 600 },
    'Annaba': { home: 900, stop: 600 },
    'Batna': { home: 900, stop: 600 },
    'Tissemsilt': { home: 900, stop: 600 },
    'Skikda': { home: 900, stop: 600 },
    'Mila': { home: 900, stop: 600 },
    'M\'Sila': { home: 900, stop: 600 },
    'El Tarf': { home: 950, stop: 600 },
    'Guelma': { home: 950, stop: 600 },
    'Khenchela': { home: 950, stop: 600 },
    'Oum El Bouaghi': { home: 950, stop: 600 },
    'Souk Ahras': { home: 950, stop: 600 },
    'Tébessa': { home: 1000, stop: 600 },
    'Laghouat': { home: 1000, stop: 600 },
    'Djelfa': { home: 1000, stop: 600 },
    'Biskra': { home: 1000, stop: 600 },
    'Ouled Djellal': { home: 1000, stop: 1000 },
    'Ghardaïa': { home: 1100, stop: 700 },
    'El Meniaa': { home: 1100, stop: 700 },
    'El Oued': { home: 1100, stop: 700 },
    'El M\'Ghair': { home: 1100, stop: 1100 },
    'Ouargla': { home: 1100, stop: 700 },
    'Touggourt': { home: 1100, stop: 700 },
    'El Bayadh': { home: 1200, stop: 800 },
    'Naâma': { home: 1200, stop: 800 },
    'Béchar': { home: 1200, stop: 800 },
    'Béni Abbès': { home: 1200, stop: 1200 },
    'Adrar': { home: 1500, stop: 1000 },
    'Timimoun': { home: 1500, stop: 1000 },
    'Tindouf': { home: 1700, stop: 1000 },
    'In Salah': { home: 1800, stop: 1200 },
    'Illizi': { home: 1900, stop: 1500 },
    'Tamanrasset': { home: 2000, stop: 1500 },
    'Djanet': { home: 2200, stop: 2200 }
};

// Global variables
let map, mapStopDesk, marker;
let stopDeskMarkers = [];
const subtotal = parseFloat(document.getElementById('subtotal-display')?.textContent?.replace(/[^\d.-]/g, '')) || 0;

// ========== Initialize on Page Load ==========
document.addEventListener('DOMContentLoaded', function() {
    initHomeMap();
    
    // Attach event listeners
    document.getElementById('wilaya')?.addEventListener('change', updateShippingCost);
    document.querySelectorAll('input[name="delivery_type"]').forEach(radio => {
        radio.addEventListener('change', handleDeliveryChange);
    });
    document.getElementById('checkoutForm')?.addEventListener('submit', validateCheckoutForm);
});

// ========== Shipping Cost Calculation ==========
function updateShippingCost() {
    const wilaya = document.getElementById('wilaya').value;
    const deliveryType = document.querySelector('input[name="delivery_type"]:checked').value;
    
    if (!wilaya) {
        document.getElementById('home-price').textContent = 'Select wilaya';
        document.getElementById('stop-price').textContent = 'Select wilaya';
        document.getElementById('shipping-cost-display').textContent = 'Select wilaya first';
        return;
    }

    const rates = shippingRates[wilaya] || { home: 800, stop: 800 };
    
    // Update price labels
    document.getElementById('home-price').textContent = rates.home + ' DZD';
    document.getElementById('stop-price').textContent = rates.stop + ' DZD (Save ' + (rates.home - rates.stop) + ' DZD!)';

    const shippingCost = deliveryType === 'stop_desk' ? rates.stop : rates.home;
    document.getElementById('shipping-cost-display').textContent = shippingCost + ' DZD';
    document.getElementById('shipping_cost').value = shippingCost;
    updateGrandTotal(shippingCost);

    // Load stop desks for selected wilaya
    if (deliveryType === 'stop_desk') {
        loadStopDesks(wilaya);
    }
}

function updateGrandTotal(shippingCost) {
    const grandTotal = subtotal + shippingCost;
    document.getElementById('grand-total-display').textContent = grandTotal + ' DZD';
}

// ========== Delivery Method Toggle ==========
function handleDeliveryChange() {
    const deliveryType = document.querySelector('input[name="delivery_type"]:checked').value;
    const homeFields = document.getElementById('home-address-fields');
    const stopFields = document.getElementById('stop-desk-fields');
    const cityInput = document.getElementById('city');
    const addressInput = document.getElementById('address');

    if (deliveryType === 'home') {
        homeFields.style.display = 'block';
        stopFields.style.display = 'none';
        cityInput.required = true;
        addressInput.required = true;
        
        // Initialize home delivery map if not done
        if (!map) {
            initHomeMap();
        }
    } else {
        homeFields.style.display = 'none';
        stopFields.style.display = 'block';
        cityInput.required = false;
        addressInput.required = false;
        
        // Initialize stop desk map if not done
        if (!mapStopDesk) {
            initStopDeskMap();
        }
        
        const wilaya = document.getElementById('wilaya').value;
        if (wilaya) {
            loadStopDesks(wilaya);
        }
    }

    updateShippingCost();
}

// ========== Home Delivery Map ==========
function initHomeMap() {
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded');
        return;
    }

    map = L.map('map').setView([36.7538, 3.0588], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        if (marker) {
            map.removeLayer(marker);
        }

        marker = L.marker([lat, lng]).addTo(map);
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;

        // Reverse geocoding
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data.address) {
                    const addr = data.address;
                    let addressText = '';
                    
                    if (addr.road) addressText += addr.road + ', ';
                    if (addr.suburb) addressText += addr.suburb + ', ';
                    if (addr.city || addr.town) addressText += (addr.city || addr.town);
                    
                    document.getElementById('address').value = addressText || data.display_name;
                    
                    if (addr.city || addr.town) {
                        document.getElementById('city').value = addr.city || addr.town;
                    }
                }
            })
            .catch(err => console.log('Geocoding error:', err));
    });

    // Get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            map.setView([lat, lng], 13);
            marker = L.marker([lat, lng]).addTo(map);
            document.getElementById('latitude').value = lat;
            document.getElementById('longitude').value = lng;
        });
    }
}

// ========== Stop Desk Map ==========
function initStopDeskMap() {
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded');
        return;
    }

    mapStopDesk = L.map('map-stop-desk').setView([36.7538, 3.0588], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(mapStopDesk);
}

function loadStopDesks(wilaya) {
    // populated from for backend
    const stopDesks = window.stopDesksData || [];
    
    // Clear existing markers
    stopDeskMarkers.forEach(m => mapStopDesk.removeLayer(m));
    stopDeskMarkers = [];

    // Filter stop desks by wilaya
    const desksInWilaya = stopDesks.filter(desk => desk.wilaya === wilaya);

    if (desksInWilaya.length === 0) {
        alert('No Stop Desks available in ' + wilaya + '. Please choose Home Delivery or select another wilaya.');
        return;
    }

    // Add markers for each stop desk
    desksInWilaya.forEach(desk => {
        const icon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        const deskMarker = L.marker([desk.lat, desk.lng], { icon: icon })
            .addTo(mapStopDesk)
            .bindPopup(`
                <div style="text-align: center;">
                    <h3 style="color: #10b981; margin-bottom: 0.5rem;">${desk.name}</h3>
                    <p style="margin: 0.3rem 0;"><strong>📍</strong> ${desk.address}</p>
                </div>
            `);

        deskMarker.on('click', function() {
            selectStopDesk(desk.id);
        });

        stopDeskMarkers.push(deskMarker);
    });

    // Fit map to show all markers
    if (desksInWilaya.length > 0) {
        const group = L.featureGroup(stopDeskMarkers);
        mapStopDesk.fitBounds(group.getBounds().pad(0.1));
    }
}

// ========== Select Stop Desk ==========
window.selectStopDesk = function(deskId) {
    const stopDesks = window.stopDesksData || [];
    const desk = stopDesks.find(d => d.id === deskId);
    if (!desk) return;

    // Update hidden input
    document.getElementById('stop_desk_id').value = deskId;

    // Update info card
    document.getElementById('desk-name').textContent = desk.name;
    document.getElementById('desk-address').textContent = desk.address + ', ' + desk.city;
    document.getElementById('desk-phone').textContent = desk.phone;
    document.getElementById('desk-hours').textContent = desk.hours + ' (' + desk.days + ')';

    // Show info card
    document.getElementById('selected-stop-desk').classList.add('active');

    // Highlight selected marker
    stopDeskMarkers.forEach(marker => {
        if (marker.getLatLng().lat === desk.lat && marker.getLatLng().lng === desk.lng) {
            marker.setIcon(L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            }));
        } else {
            marker.setIcon(L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            }));
        }
    });
};

// ========== Form Validation ==========
function validateCheckoutForm(e) {
    const deliveryType = document.querySelector('input[name="delivery_type"]:checked').value;
    
    if (deliveryType === 'stop_desk') {
        const stopDeskId = document.getElementById('stop_desk_id').value;
        if (!stopDeskId) {
            e.preventDefault();
            alert('Please select a Stop Desk location on the map');
            return false;
        }
    }
}