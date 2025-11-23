/**
 * MOBILE UX ENHANCEMENTS
 * Optimizado para dispositivos móviles (80% usuarios Ecuador)
 */

// ===========================
// DETECCIÓN DE DISPOSITIVO
// ===========================

const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
const isAndroid = /Android/.test(navigator.userAgent);

// ===========================
// MENU HAMBURGUESA
// ===========================

document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('active');
            // Cambiar icono
            this.innerHTML = navbarMenu.classList.contains('active') ? '✕' : '☰';
        });

        // Cerrar menú al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.navbar')) {
                navbarMenu.classList.remove('active');
                if (navbarToggle) {
                    navbarToggle.innerHTML = '☰';
                }
            }
        });
    }
});

// ===========================
// FILTROS COLAPSABLES
// ===========================

function initFilters() {
    const filterToggles = document.querySelectorAll('.filter-toggle');

    filterToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const content = this.nextElementSibling;
            content.classList.toggle('active');

            // Rotar icono
            const icon = this.querySelector('.filter-icon');
            if (icon) {
                icon.style.transform = content.classList.contains('active')
                    ? 'rotate(180deg)'
                    : 'rotate(0deg)';
            }
        });
    });
}

// ===========================
// WISHLIST (FAVORITOS)
// ===========================

function toggleWishlist(productId, buttonElement) {
    if (!buttonElement) return;

    // Animación de loading
    const originalHTML = buttonElement.innerHTML;
    buttonElement.innerHTML = '<span class="loading-spinner"></span>';
    buttonElement.disabled = true;

    fetch('/perfil/wishlist/toggle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ producto_id: productId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar icono
            if (data.added) {
                buttonElement.innerHTML = '❤️'; // Corazón lleno
                buttonElement.classList.add('in-wishlist');
                showToast('Agregado a favoritos');
            } else {
                buttonElement.innerHTML = '🤍'; // Corazón vacío
                buttonElement.classList.remove('in-wishlist');
                showToast('Eliminado de favoritos');
            }

            // Animación de éxito
            buttonElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                buttonElement.style.transform = 'scale(1)';
            }, 200);
        } else {
            buttonElement.innerHTML = originalHTML;
            showToast(data.message || 'Error al actualizar favoritos', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        buttonElement.innerHTML = originalHTML;
        showToast('Error de conexión', 'error');
    })
    .finally(() => {
        buttonElement.disabled = false;
    });
}

// ===========================
// ADD TO CART (AGREGAR AL CARRITO)
// ===========================

function addToCart(productId, quantity = 1) {
    const btn = event.target.closest('.add-to-cart-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="loading-spinner"></span>';
    }

    fetch('/carrito/agregar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            producto_id: productId,
            cantidad: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Producto agregado al carrito');
            updateCartBadge(data.cart_count);

            // Vibración táctil (si está disponible)
            if ('vibrate' in navigator) {
                navigator.vibrate(50);
            }

            // Animación del botón
            if (btn) {
                btn.innerHTML = '✓ Agregado';
                btn.classList.add('btn-success');
                setTimeout(() => {
                    btn.innerHTML = 'Agregar al Carrito';
                    btn.classList.remove('btn-success');
                    btn.disabled = false;
                }, 2000);
            }
        } else {
            showToast(data.message || 'Error al agregar producto', 'error');
            if (btn) {
                btn.innerHTML = 'Agregar al Carrito';
                btn.disabled = false;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
        if (btn) {
            btn.innerHTML = 'Agregar al Carrito';
            btn.disabled = false;
        }
    });
}

// ===========================
// TOAST NOTIFICATIONS
// ===========================

function showToast(message, type = 'success') {
    // Eliminar toasts anteriores
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Auto-hide después de 3 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);

    // Vibración para feedback táctil
    if ('vibrate' in navigator) {
        navigator.vibrate(type === 'error' ? [50, 50, 50] : 50);
    }
}

// ===========================
// UPDATE CART BADGE
// ===========================

function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';

        // Animación
        badge.style.transform = 'scale(1.3)';
        setTimeout(() => {
            badge.style.transform = 'scale(1)';
        }, 200);
    }
}

// ===========================
// INFINITE SCROLL (Lazy Loading)
// ===========================

let loading = false;
let currentPage = 1;
let hasMore = true;

function initInfiniteScroll() {
    if (!document.querySelector('.product-grid')) return;

    window.addEventListener('scroll', function() {
        if (loading || !hasMore) return;

        const scrollPosition = window.scrollY + window.innerHeight;
        const pageHeight = document.documentElement.scrollHeight;

        // Cargar más cuando falta 300px para el final
        if (scrollPosition >= pageHeight - 300) {
            loadMoreProducts();
        }
    });
}

function loadMoreProducts() {
    loading = true;
    const loader = document.createElement('div');
    loader.className = 'text-center p-3';
    loader.innerHTML = '<div class="loading-spinner"></div>';
    document.querySelector('.product-grid').appendChild(loader);

    currentPage++;
    const url = new URL(window.location.href);
    url.searchParams.set('page', currentPage);

    fetch(url)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newProducts = doc.querySelectorAll('.product-card');

            if (newProducts.length === 0) {
                hasMore = false;
                loader.innerHTML = '<p>No hay más productos</p>';
            } else {
                newProducts.forEach(product => {
                    document.querySelector('.product-grid').appendChild(product);
                });
                loader.remove();
            }
        })
        .catch(error => {
            console.error('Error loading products:', error);
            loader.remove();
        })
        .finally(() => {
            loading = false;
        });
}

// ===========================
// PULL TO REFRESH
// ===========================

let pullStartY = 0;
let pullMoveY = 0;
let isPulling = false;

function initPullToRefresh() {
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            pullStartY = e.touches[0].clientY;
            isPulling = true;
        }
    }, { passive: true });

    document.addEventListener('touchmove', function(e) {
        if (!isPulling) return;

        pullMoveY = e.touches[0].clientY;
        const pullDistance = pullMoveY - pullStartY;

        if (pullDistance > 80 && window.scrollY === 0) {
            // Mostrar indicador de refresh
            document.body.style.paddingTop = '50px';
        }
    }, { passive: true });

    document.addEventListener('touchend', function() {
        if (!isPulling) return;

        const pullDistance = pullMoveY - pullStartY;
        if (pullDistance > 80 && window.scrollY === 0) {
            window.location.reload();
        }

        document.body.style.paddingTop = '0';
        isPulling = false;
    });
}

// ===========================
// SWIPE GESTURES PARA NAVEGACIÓN
// ===========================

let touchStartX = 0;
let touchEndX = 0;

function initSwipeNavigation() {
    const images = document.querySelectorAll('.product-image-gallery');
    if (images.length === 0) return;

    images.forEach(gallery => {
        gallery.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        gallery.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe(gallery);
        }, { passive: true });
    });
}

function handleSwipe(element) {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - next image
            element.dispatchEvent(new CustomEvent('swipe-left'));
        } else {
            // Swipe right - previous image
            element.dispatchEvent(new CustomEvent('swipe-right'));
        }
    }
}

// ===========================
// OPTIMIZACIÓN DE IMÁGENES
// ===========================

function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// ===========================
// STICKY HEADER HIDE ON SCROLL
// ===========================

let lastScrollY = window.scrollY;

function initStickyHeader() {
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        if (window.scrollY > lastScrollY && window.scrollY > 100) {
            // Scrolling down
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            navbar.style.transform = 'translateY(0)';
        }

        lastScrollY = window.scrollY;
    }, { passive: true });
}

// ===========================
// BOTÓN SCROLL TO TOP
// ===========================

function initScrollToTop() {
    const btn = document.createElement('button');
    btn.className = 'scroll-to-top';
    btn.innerHTML = '↑';
    btn.style.cssText = `
        position: fixed;
        bottom: 80px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #007bff;
        color: white;
        border: none;
        font-size: 24px;
        display: none;
        z-index: 998;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(btn);

    window.addEventListener('scroll', function() {
        btn.style.display = window.scrollY > 500 ? 'block' : 'none';
    });

    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ===========================
// INICIALIZACIÓN
// ===========================

document.addEventListener('DOMContentLoaded', function() {
    initFilters();
    initLazyLoading();

    if (isMobile) {
        initInfiniteScroll();
        initPullToRefresh();
        initSwipeNavigation();
        initStickyHeader();
        initScrollToTop();
    }
});

// ===========================
// EXPORTAR FUNCIONES GLOBALES
// ===========================

window.toggleWishlist = toggleWishlist;
window.addToCart = addToCart;
window.showToast = showToast;
