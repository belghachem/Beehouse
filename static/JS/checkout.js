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
let map, marker;
const subtotal = parseFloat(document.getElementById('subtotal-display')?.textContent?.replace(/[^\d.-]/g, '')) || 0;

// ========== Initialize on Page Load ==========
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
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
}

function updateGrandTotal(shippingCost) {
    const grandTotal = subtotal + shippingCost;
    document.getElementById('grand-total-display').textContent = grandTotal + ' DZD';
}

// ========== Delivery Method Toggle ==========
function handleDeliveryChange() {
    const deliveryType = document.querySelector('input[name="delivery_type"]:checked').value;
    const addressFields = document.getElementById('address-fields');
    const cityInput = document.getElementById('city');
    const addressInput = document.getElementById('address');

    // Both delivery types need address information
    addressFields.style.display = 'block';
    cityInput.required = true;
    addressInput.required = true;

    // Show info message for stop desk
    const stopDeskInfo = document.getElementById('stop-desk-info');
    if (stopDeskInfo) {
        stopDeskInfo.style.display = deliveryType === 'stop_desk' ? 'block' : 'none';
    }

    updateShippingCost();
}

// ========== Single Map for Address Selection ==========
function initMap() {
    if (typeof L === 'undefined') {
        console.error('Leaflet library not loaded');
        return;
    }

    map = L.map('map').setView([36.7538, 3.0588], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Click to set location
    map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        if (marker) {
            map.removeLayer(marker);
        }

        marker = L.marker([lat, lng]).addTo(map);
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lng;

        // Reverse geocoding to get address
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

    // Get user's current location
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

// ========== Form Validation ==========
function validateCheckoutForm(e) {
    const wilaya = document.getElementById('wilaya').value;
    const city = document.getElementById('city').value;
    const address = document.getElementById('address').value;
    const phone = document.getElementById('phone').value;
    
    if (!wilaya) {
        e.preventDefault();
        alert('Please select your wilaya');
        return false;
    }
    
    if (!city || !address) {
        e.preventDefault();
        alert('Please provide your complete address');
        return false;
    }
    
    if (!phone) {
        e.preventDefault();
        alert('Please provide your phone number');
        return false;
    }
    
    return true;
}