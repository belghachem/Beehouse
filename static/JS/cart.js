// ========== Quantity Controls ==========
function increaseQuantity(btn) {
    const input = btn.parentElement.querySelector('.quantity-input');
    const updateBtn = btn.parentElement.querySelector('.btn-update');
    
    if (input.value < 99) {
        input.value = parseInt(input.value) + 1;
        updateBtn.style.display = 'inline-block';
    }
}

function decreaseQuantity(btn) {
    const input = btn.parentElement.querySelector('.quantity-input');
    const updateBtn = btn.parentElement.querySelector('.btn-update');
    
    if (input.value > 1) {
        input.value = parseInt(input.value) - 1;
        updateBtn.style.display = 'inline-block';
    }
}

// ========== Update Cart Item (with Loading State) ==========
function updateCartItem(form) {
    const submitBtn = form.querySelector('.btn-update');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Updating...';
    
    // Form will submit naturally, but we add a visual indicator
    setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }, 3000);
}

// ========== Remove Item Confirmation ==========
function confirmRemove(itemName) {
    return confirm(`Remove "${itemName}" from your cart?`);
}

// ========== Cart Summary Calculations ==========
function updateCartSummary() {
    const cartItems = document.querySelectorAll('.cart-table tbody tr');
    let subtotal = 0;
    
    cartItems.forEach(row => {
        const priceCell = row.querySelector('.product-price');
        const quantityInput = row.querySelector('.quantity-input');
        
        if (priceCell && quantityInput) {
            const price = parseFloat(priceCell.textContent.replace(/[^\d.-]/g, ''));
            const quantity = parseInt(quantityInput.value);
            subtotal += price * quantity;
        }
    });
    
    // Update display
    const grandTotalEl = document.getElementById('grand-total-display');
    if (grandTotalEl) {
        grandTotalEl.textContent = subtotal + ' DZD';
    }
}

// ========== Auto-update on Quantity Change ==========
document.addEventListener('DOMContentLoaded', function() {
    // Monitor quantity input changes
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const updateBtn = this.parentElement.querySelector('.btn-update');
            if (updateBtn) {
                updateBtn.style.display = 'inline-block';
            }
        });
    });
    
    // Update button click handler
    document.querySelectorAll('.btn-update').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const form = this.closest('form');
            updateCartItem(form);
        });
    });
    
    // Initial summary calculation
    updateCartSummary();
});

// ========== Empty Cart Check ==========
function checkEmptyCart() {
    const cartTable = document.querySelector('.cart-table tbody');
    
    if (cartTable && cartTable.children.length === 0) {
        // Show empty cart message
        const emptyMessage = `
            <div class="empty-cart">
                <div class="empty-cart-icon">🛒</div>
                <h2>Your Cart is Empty</h2>
                <p>Looks like you haven't added anything to your cart yet.</p>
                <a href="/products/" class="shop-now-btn">Start Shopping 🍯</a>
            </div>
        `;
        
        const cartContainer = document.querySelector('.cart-container');
        if (cartContainer) {
            cartContainer.innerHTML = emptyMessage;
        }
    }
}

// ========== Toast Notification for Cart Actions ==========
function showCartToast(message, type = 'success') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `cart-toast cart-toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Add CSS animations
if (!document.querySelector('#cart-toast-styles')) {
    const style = document.createElement('style');
    style.id = 'cart-toast-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// ========== Prevent Accidental Cart Clear ==========
window.addEventListener('beforeunload', function(e) {
    const cartItems = document.querySelectorAll('.cart-table tbody tr');
    
    if (cartItems.length > 0) {
        const hasUnsavedChanges = Array.from(document.querySelectorAll('.btn-update')).some(btn => {
            return btn.style.display !== 'none';
        });
        
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes to your cart. Are you sure you want to leave?';
            return e.returnValue;
        }
    }
});
function mobileIncreaseQty(btn) {
            const input = btn.parentElement.querySelector('.mobile-qty-input');
            const itemId = extractItemId(input);
            
            if (input.value < 99) {
                input.value = parseInt(input.value) + 1;
                updateHiddenInput(itemId, input.value);
                showMobileUpdateBtn(input);
            }
        }

        function mobileDecreaseQty(btn) {
            const input = btn.parentElement.querySelector('.mobile-qty-input');
            const itemId = extractItemId(input);
            
            if (input.value > 1) {
                input.value = parseInt(input.value) - 1;
                updateHiddenInput(itemId, input.value);
                showMobileUpdateBtn(input);
            }
        }

        function showMobileUpdateBtn(input) {
            const card = input.closest('.mobile-cart-card');
            const updateBtn = card.querySelector('.mobile-update-btn');
            const itemId = extractItemId(input);
            
            updateBtn.classList.add('show');
            updateHiddenInput(itemId, input.value);
        }

        function extractItemId(input) {
            const form = input.closest('form');
            const action = form.getAttribute('action');
            return action.match(/\/(\d+)\//)[1];
        }

        function updateHiddenInput(itemId, value) {
            const hiddenInput = document.getElementById(`hidden-qty-${itemId}`);
            if (hiddenInput) {
                hiddenInput.value = value;
            }
        }