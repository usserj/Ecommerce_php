/**
 * Main JavaScript - Tienda Virtual
 * Handles cart operations, wishlist, AJAX calls, and UI interactions
 */

(function() {
    'use strict';

    // ===========================
    // Shopping Cart Functions
    // ===========================

    /**
     * Add product to cart via AJAX
     */
    window.addToCart = function(productId, quantity = 1) {
        quantity = parseInt(quantity) || 1;

        // Show loading state
        showLoading();

        fetch('/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                producto_id: productId,
                cantidad: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showAlert('success', data.message || 'Producto agregado al carrito');
                updateCartBadge(data.cart_count);

                // Update cart dropdown if exists
                if (data.cart_html) {
                    updateCartDropdown(data.cart_html);
                }
            } else {
                showAlert('danger', data.message || 'Error al agregar el producto');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showAlert('danger', 'Error al agregar el producto al carrito');
        });
    };

    /**
     * Update cart item quantity
     */
    window.updateCartQuantity = function(productId, quantity) {
        quantity = parseInt(quantity);
        if (quantity < 1) {
            removeFromCart(productId);
            return;
        }

        fetch('/cart/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                producto_id: productId,
                cantidad: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update item total
                updateItemTotal(productId, data.item_total);
                // Update cart summary
                updateCartSummary(data.cart_summary);
                updateCartBadge(data.cart_count);
            } else {
                showAlert('danger', data.message || 'Error al actualizar el carrito');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Error al actualizar el carrito');
        });
    };

    /**
     * Remove product from cart
     */
    window.removeFromCart = function(productId) {
        if (!confirm('¿Estás seguro de eliminar este producto del carrito?')) {
            return;
        }

        showLoading();

        fetch('/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                producto_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                // Remove item from DOM
                const itemElement = document.querySelector(`[data-product-id="${productId}"]`);
                if (itemElement) {
                    itemElement.remove();
                }

                // Update cart summary
                updateCartSummary(data.cart_summary);
                updateCartBadge(data.cart_count);

                showAlert('success', data.message || 'Producto eliminado del carrito');

                // Show empty cart message if no items
                if (data.cart_count === 0) {
                    location.reload();
                }
            } else {
                showAlert('danger', data.message || 'Error al eliminar el producto');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showAlert('danger', 'Error al eliminar el producto');
        });
    };

    /**
     * Clear entire cart
     */
    window.clearCart = function() {
        if (!confirm('¿Estás seguro de vaciar todo el carrito?')) {
            return;
        }

        showLoading();

        fetch('/cart/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                location.reload();
            } else {
                showAlert('danger', data.message || 'Error al vaciar el carrito');
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            showAlert('danger', 'Error al vaciar el carrito');
        });
    };

    // ===========================
    // Wishlist Functions
    // ===========================

    /**
     * Toggle product in wishlist
     */
    window.toggleWishlist = function(productId, button) {
        if (!isUserLoggedIn()) {
            showAlert('warning', 'Debes iniciar sesión para agregar a favoritos');
            setTimeout(() => {
                window.location.href = '/auth/login';
            }, 1500);
            return;
        }

        const icon = button.querySelector('i');
        const isInWishlist = icon.classList.contains('fas');

        fetch('/profile/wishlist/toggle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                producto_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Toggle icon
                if (data.added) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    button.classList.add('active');
                    showAlert('success', 'Producto agregado a favoritos');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    button.classList.remove('active');
                    showAlert('info', 'Producto eliminado de favoritos');
                }
            } else {
                showAlert('danger', data.message || 'Error al actualizar favoritos');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Error al actualizar favoritos');
        });
    };

    // ===========================
    // Product Detail Functions
    // ===========================

    /**
     * Initialize quantity controls
     */
    function initQuantityControls() {
        const qtyInput = document.getElementById('quantity');
        const increaseBtn = document.getElementById('increaseQty');
        const decreaseBtn = document.getElementById('decreaseQty');

        if (increaseBtn) {
            increaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(qtyInput.value) || 1;
                qtyInput.value = currentValue + 1;
            });
        }

        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(qtyInput.value) || 1;
                if (currentValue > 1) {
                    qtyInput.value = currentValue - 1;
                }
            });
        }

        // Prevent invalid input
        if (qtyInput) {
            qtyInput.addEventListener('input', function() {
                const value = parseInt(this.value);
                if (isNaN(value) || value < 1) {
                    this.value = 1;
                }
            });
        }
    }

    /**
     * Add to cart from product detail page
     */
    function initAddToCartButton() {
        const addToCartBtn = document.getElementById('addToCartBtn');
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function() {
                const productId = this.dataset.productId;
                const qtyInput = document.getElementById('quantity');
                const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

                addToCart(productId, quantity);
            });
        }
    }

    // ===========================
    // Comment/Review Functions
    // ===========================

    /**
     * Submit product comment
     */
    function initCommentForm() {
        const commentForm = document.getElementById('commentForm');
        if (commentForm) {
            commentForm.addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(this);
                const productId = this.dataset.productId;

                showLoading();

                fetch(`/shop/product/${productId}/comment`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    if (data.success) {
                        showAlert('success', 'Comentario enviado correctamente');
                        this.reset();

                        // Reload comments section
                        if (data.comment_html) {
                            const commentsContainer = document.getElementById('commentsContainer');
                            if (commentsContainer) {
                                commentsContainer.insertAdjacentHTML('afterbegin', data.comment_html);
                            }
                        }
                    } else {
                        showAlert('danger', data.message || 'Error al enviar el comentario');
                    }
                })
                .catch(error => {
                    hideLoading();
                    console.error('Error:', error);
                    showAlert('danger', 'Error al enviar el comentario');
                });
            });
        }
    }

    /**
     * Star rating interaction
     */
    function initStarRating() {
        const stars = document.querySelectorAll('.star-rating-input i');
        const ratingInput = document.getElementById('calificacion');

        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                const rating = index + 1;
                ratingInput.value = rating;

                // Update visual state
                stars.forEach((s, i) => {
                    if (i < rating) {
                        s.classList.remove('far');
                        s.classList.add('fas');
                    } else {
                        s.classList.remove('fas');
                        s.classList.add('far');
                    }
                });
            });

            star.addEventListener('mouseenter', function() {
                const rating = index + 1;
                stars.forEach((s, i) => {
                    if (i < rating) {
                        s.classList.add('text-warning');
                    }
                });
            });

            star.addEventListener('mouseleave', function() {
                stars.forEach(s => {
                    s.classList.remove('text-warning');
                });
            });
        });
    }

    // ===========================
    // Search Functions
    // ===========================

    /**
     * Initialize search functionality
     */
    function initSearch() {
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                const searchInput = this.querySelector('input[name="q"]');
                if (!searchInput.value.trim()) {
                    e.preventDefault();
                    showAlert('warning', 'Por favor ingresa un término de búsqueda');
                }
            });
        }
    }

    // ===========================
    // Checkout Functions
    // ===========================

    /**
     * Initialize payment method selection
     */
    function initPaymentMethods() {
        const paymentMethods = document.querySelectorAll('.payment-method');
        paymentMethods.forEach(method => {
            method.addEventListener('click', function() {
                paymentMethods.forEach(m => m.classList.remove('selected'));
                this.classList.add('selected');
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                }
            });
        });
    }

    /**
     * Validate checkout form
     */
    function initCheckoutForm() {
        const checkoutForm = document.getElementById('checkoutForm');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', function(e) {
                const paymentMethod = this.querySelector('input[name="metodo_pago"]:checked');
                if (!paymentMethod) {
                    e.preventDefault();
                    showAlert('warning', 'Por favor selecciona un método de pago');
                    return false;
                }
            });
        }
    }

    // ===========================
    // Profile Functions
    // ===========================

    /**
     * Preview image before upload
     */
    function initImagePreview() {
        const imageInput = document.getElementById('foto');
        const imagePreview = document.getElementById('imagePreview');

        if (imageInput && imagePreview) {
            imageInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        imagePreview.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    /**
     * Delete account confirmation
     */
    function initDeleteAccount() {
        const deleteBtn = document.getElementById('deleteAccountBtn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function(e) {
                const confirmation = confirm('¿Estás seguro de eliminar tu cuenta? Esta acción no se puede deshacer.');
                if (!confirmation) {
                    e.preventDefault();
                }
            });
        }
    }

    // ===========================
    // Utility Functions
    // ===========================

    /**
     * Get CSRF token from meta tag or cookie
     */
    function getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        if (token) {
            return token.getAttribute('content');
        }

        // Fallback: get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return value;
            }
        }

        return '';
    }

    /**
     * Check if user is logged in
     */
    function isUserLoggedIn() {
        // Check for user-specific elements or data attributes
        return document.querySelector('[data-user-logged-in]') !== null;
    }

    /**
     * Update cart badge count
     */
    function updateCartBadge(count) {
        const badge = document.querySelector('.cart-icon .badge');
        if (badge) {
            badge.textContent = count;
            if (count === 0) {
                badge.style.display = 'none';
            } else {
                badge.style.display = 'inline-block';
            }
        }
    }

    /**
     * Update cart dropdown (if exists)
     */
    function updateCartDropdown(html) {
        const dropdown = document.getElementById('cartDropdown');
        if (dropdown) {
            dropdown.innerHTML = html;
        }
    }

    /**
     * Update item total in cart
     */
    function updateItemTotal(productId, total) {
        const totalElement = document.querySelector(`[data-product-id="${productId}"] .item-total`);
        if (totalElement) {
            totalElement.textContent = `$${total.toFixed(2)}`;
        }
    }

    /**
     * Update cart summary (subtotal, tax, shipping, total)
     */
    function updateCartSummary(summary) {
        if (summary.subtotal !== undefined) {
            const subtotalElement = document.getElementById('cartSubtotal');
            if (subtotalElement) {
                subtotalElement.textContent = `$${summary.subtotal.toFixed(2)}`;
            }
        }

        if (summary.tax !== undefined) {
            const taxElement = document.getElementById('cartTax');
            if (taxElement) {
                taxElement.textContent = `$${summary.tax.toFixed(2)}`;
            }
        }

        if (summary.shipping !== undefined) {
            const shippingElement = document.getElementById('cartShipping');
            if (shippingElement) {
                shippingElement.textContent = `$${summary.shipping.toFixed(2)}`;
            }
        }

        if (summary.total !== undefined) {
            const totalElement = document.getElementById('cartTotal');
            if (totalElement) {
                totalElement.textContent = `$${summary.total.toFixed(2)}`;
            }
        }
    }

    /**
     * Show alert message
     */
    function showAlert(type, message) {
        const alertsContainer = document.getElementById('alertsContainer') || createAlertsContainer();

        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertsContainer.appendChild(alert);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    /**
     * Create alerts container if it doesn't exist
     */
    function createAlertsContainer() {
        const container = document.createElement('div');
        container.id = 'alertsContainer';
        container.style.position = 'fixed';
        container.style.top = '80px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.maxWidth = '400px';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Show loading overlay
     */
    function showLoading() {
        let overlay = document.getElementById('loadingOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'spinner-overlay';
            overlay.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden">Cargando...</span></div>';
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    }

    /**
     * Hide loading overlay
     */
    function hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    /**
     * Format price
     */
    function formatPrice(price) {
        return `$${parseFloat(price).toFixed(2)}`;
    }

    /**
     * Debounce function for search/filter inputs
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Smooth scroll to element
     */
    function scrollToElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // ===========================
    // Initialization
    // ===========================

    /**
     * Initialize all functionality on DOM ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize quantity controls
        initQuantityControls();

        // Initialize add to cart button
        initAddToCartButton();

        // Initialize comment form
        initCommentForm();

        // Initialize star rating
        initStarRating();

        // Initialize search
        initSearch();

        // Initialize payment methods
        initPaymentMethods();

        // Initialize checkout form
        initCheckoutForm();

        // Initialize image preview
        initImagePreview();

        // Initialize delete account
        initDeleteAccount();

        // Cart quantity inputs with debounce
        const qtyInputs = document.querySelectorAll('.cart-quantity-input');
        qtyInputs.forEach(input => {
            input.addEventListener('input', debounce(function() {
                const productId = this.dataset.productId;
                const quantity = parseInt(this.value);
                updateCartQuantity(productId, quantity);
            }, 500));
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href !== '#') {
                    e.preventDefault();
                    scrollToElement(href);
                }
            });
        });

        // Auto-hide alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    });

    // Export functions to global scope for inline onclick handlers
    window.APP = {
        addToCart,
        updateCartQuantity,
        removeFromCart,
        clearCart,
        toggleWishlist,
        showAlert,
        showLoading,
        hideLoading
    };

})();
