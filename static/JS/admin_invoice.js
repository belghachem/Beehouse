document.addEventListener('DOMContentLoaded', function() {
    // Check if user is staff/admin (you'll need to pass this from Django context)
    const isStaff = document.body.dataset.isStaff === 'true' || document.body.dataset.isAdmin === 'true';
    
    if (isStaff) {
        addViewInvoiceButton();
    }
});

function addViewInvoiceButton() {
    // Find the action buttons container
    const actionButtons = document.querySelector('.action-buttons');
    
    if (!actionButtons) {
        console.warn('Action buttons container not found');
        return;
    }
    
    // Get the order ID from the page
    const orderIdElement = document.querySelector('.page-header h1');
    const orderIdText = orderIdElement?.textContent || '';
    const orderIdMatch = orderIdText.match(/#(\d+)/);
    const orderId = orderIdMatch ? orderIdMatch[1] : null;
    
    if (!orderId) {
        console.warn('Order ID not found');
        return;
    }
    
    // Create the "View Invoice" button
    const viewInvoiceBtn = document.createElement('a');
    viewInvoiceBtn.href = `/orders/print/${orderId}/`; // Adjust URL as needed
    viewInvoiceBtn.target = '_blank'; // Open in new tab
    viewInvoiceBtn.className = 'btn btn-view-invoice';
    viewInvoiceBtn.innerHTML = 'View Invoice';
    viewInvoiceBtn.style.cssText = `
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
    `;
    
    // Add hover effect
    viewInvoiceBtn.addEventListener('mouseenter', function() {
        this.style.background = 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)';
    });
    
    viewInvoiceBtn.addEventListener('mouseleave', function() {
        this.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
    });
    
    // Insert the button (second position, after "Back to Orders")
    if (actionButtons.children.length >= 1) {
        actionButtons.insertBefore(viewInvoiceBtn, actionButtons.children[1]);
    } else {
        actionButtons.appendChild(viewInvoiceBtn);
    }
}

// Alternative: Add button using CSS injection (cleaner)
function addViewInvoiceButtonCSS() {
    const orderId = getOrderIdFromPage();
    
    if (!orderId) return;
    
    const style = document.createElement('style');
    style.textContent = `
        .action-buttons::after {
            content: 'View Invoice';
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            order: 2; /* Position after first button */
        }
        
        .action-buttons::after:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            transform: translateY(-2px);
        }
    `;
    
    document.head.appendChild(style);
}

function getOrderIdFromPage() {
    const orderIdElement = document.querySelector('.page-header h1');
    const orderIdText = orderIdElement?.textContent || '';
    const orderIdMatch = orderIdText.match(/#(\d+)/);
    return orderIdMatch ? orderIdMatch[1] : null;
}