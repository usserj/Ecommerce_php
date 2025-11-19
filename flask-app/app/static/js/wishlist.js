/**
 * Wishlist functionality - works on all pages with product cards
 * Uses event delegation to handle dynamically loaded products
 */

// Use event delegation on document to catch all wishlist button clicks
document.addEventListener('click', function(e) {
    // Check if clicked element or its parent is a wishlist button
    const button = e.target.closest('.add-to-wishlist');

    if (!button) return; // Not a wishlist button, ignore

    e.preventDefault();
    e.stopPropagation();

    const productId = button.getAttribute('data-product-id');

    if (!productId) {
        console.error('No product ID found on wishlist button');
        showAlert('Error: No se pudo identificar el producto', 'error');
        return;
    }

    // Disable button temporarily
    button.disabled = true;
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';

    // Send request to toggle wishlist
    fetch('/perfil/wishlist/toggle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            producto_id: parseInt(productId)
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update button appearance
            if (data.added) {
                button.innerHTML = '<i class="fas fa-heart"></i> En Lista de Deseos';
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-danger');
            } else {
                button.innerHTML = '<i class="far fa-heart"></i> Lista de Deseos';
                button.classList.remove('btn-danger');
                button.classList.add('btn-outline-danger');
            }

            // Show success message
            showAlert(data.message, 'success');
        } else {
            // Restore original button state on error
            button.innerHTML = originalHTML;
            showAlert(data.message || 'Error al procesar solicitud', 'error');
        }
    })
    .catch(error => {
        console.error('Wishlist error:', error);
        button.innerHTML = originalHTML;
        showAlert('Error de conexión. Intenta de nuevo.', 'error');
    })
    .finally(() => {
        // Re-enable button
        button.disabled = false;
    });
});

/**
 * Show alert message (uses Bootstrap toast if available, otherwise alert)
 */
function showAlert(message, type = 'info') {
    // Try to use Bootstrap toast if available
    const toastContainer = document.getElementById('toast-container');

    if (toastContainer) {
        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';

        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();

        // Remove toast after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    } else {
        // Fallback to regular alert
        alert(message);
    }
}

// Initialize wishlist buttons on page load (for checking initial state)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Wishlist script loaded');
});
