/**
 * Shopping Cart Functionality
 * Handles cart operations with AJAX
 */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Add item to cart with visual feedback
 * @param {number} productId - Product ID to add
 * @param {number} qty - Quantity to add (default: 1)
 */
async function addToCart(productId, qty = 1) {
  try {
    const csrftoken = getCookie('csrftoken');
    const response = await fetch('/api/cart/add/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        product_id: productId,
        qty: qty
      })
    });

    const data = await response.json();

    if (response.ok && data.cart_count !== undefined) {
      // Update all cart count elements
      document.querySelectorAll('.cart-count').forEach(el => {
        el.textContent = data.cart_count;
      });

      // Show success notification
      showNotification('Product added to cart!', 'success');
    } else if (!response.ok) {
      showNotification(data.message || 'Failed to add to cart', 'error');
    }
  } catch (error) {
    console.error('Error adding to cart:', error);
    showNotification('An error occurred. Please try again.', 'error');
  }
}

/**
 * Remove item from cart
 * @param {number} itemId - Cart item ID to remove
 */
async function removeFromCart(itemId) {
  try {
    const csrftoken = getCookie('csrftoken');
    const response = await fetch('/api/cart/remove/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        item_id: itemId
      })
    });

    if (response.ok) {
      showNotification('Item removed from cart', 'success');
      setTimeout(() => location.reload(), 500);
    } else {
      showNotification('Failed to remove item', 'error');
    }
  } catch (error) {
    console.error('Error removing from cart:', error);
    showNotification('An error occurred', 'error');
  }
}

/**
 * Show temporary notification to user
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, warning, info)
 */
/**
 * Show temporary notification to user
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
  // Use the high-quality notification system from base.html if available
  if (typeof window.showCartNotification === 'function') {
    window.showCartNotification(message, type);
    return;
  }

  const notificationDiv = document.createElement('div');
  notificationDiv.className = `alert alert-${type === 'info' ? 'primary' : type}`;
  notificationDiv.setAttribute('role', 'alert');
  notificationDiv.textContent = message;
  notificationDiv.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
    animation: slideInRight 0.3s ease;
  `;

  document.body.appendChild(notificationDiv);

  // Auto-remove after 3 seconds
  setTimeout(() => {
    notificationDiv.style.opacity = '0';
    notificationDiv.style.transition = 'opacity 0.3s ease';
    setTimeout(() => notificationDiv.remove(), 300);
  }, 3000);
}

/**
 * Add item to wishlist with visual feedback
 * @param {number} productId - Product ID to add to wishlist
 */
async function addToWishlist(productId, button = null) {
  try {
    const csrftoken = getCookie('csrftoken');
    const response = await fetch(`/customer/wishlist/add/${productId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    });

    const data = await response.json();

    if (data.ok) {
      showNotification('✓ Added to wishlist!', 'success');
      // Update button appearance if provided
      if (button) {
        button.classList.add('in-wishlist');
        button.title = 'Added to wishlist';
        button.style.color = '#ff6b6b';
      }
    } else {
      showNotification(data.message || 'Already in wishlist', 'warning');
      // If already in wishlist, update button
      if (button && data.message && data.message.includes('already')) {
        button.classList.add('in-wishlist');
        button.style.color = '#ff6b6b';
      }
    }
    
    // Update wishlist count header if present
    if (data.wishlist_count !== undefined) {
      document.querySelectorAll('.wishlist-count').forEach(el => {
        el.textContent = data.wishlist_count;
      });
    }
  } catch (error) {
    console.error('Error adding to wishlist:', error);
    showNotification('Please login to add to wishlist', 'warning');
  }
}

/**
 * Remove item from wishlist with visual feedback
 * @param {number} productId - Product ID to remove from wishlist
 * @param {HTMLElement} button - The button element that triggered the action
 */
async function removeFromWishlist(productId, button = null) {
  try {
    const csrftoken = getCookie('csrftoken');
    const response = await fetch(`/customer/wishlist/remove/${productId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }
    });

    const data = await response.json();

    if (data.ok) {
      showNotification('Removed from wishlist', 'success');
      // Update button appearance if provided
      if (button) {
        button.classList.remove('in-wishlist');
        button.title = 'Add to wishlist';
        button.style.color = '';
      }
      // For wishlist page, remove the card
      if (button && button.closest('.card')) {
        const card = button.closest('.card');
        card.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
          card.parentElement.removeChild(card);
          // Reload if no items left
          const itemsRemaining = document.querySelectorAll('.card[class*="card-product"]').length;
          if (itemsRemaining === 0) {
            setTimeout(() => location.reload(), 500);
          }
        }, 300);
      }
    } else {
      showNotification(data.message || 'Failed to remove', 'error');
    }
    
    // Update wishlist count header if present
    if (data.wishlist_count !== undefined) {
      document.querySelectorAll('.wishlist-count').forEach(el => {
        el.textContent = data.wishlist_count;
      });
    }
  } catch (error) {
    console.error('Error removing from wishlist:', error);
    showNotification('An error occurred', 'error');
  }
}

/**
 * Initialize cart event listeners
 */
document.addEventListener('DOMContentLoaded', function () {
  // Add to cart buttons
  document.querySelectorAll('.add-to-cart').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      const productId = el.getAttribute('data-product-id');
      if (productId) {
        addToCart(parseInt(productId, 10));
      }
    });
  });

  // Add to cart buttons with add-to-cart-btn class
  document.querySelectorAll('.add-to-cart-btn').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      const productId = el.getAttribute('data-product-id');
      if (productId) {
        addToCart(parseInt(productId, 10));
      }
    });
  });

  // Add to wishlist buttons with add-to-wishlist-btn class
  document.querySelectorAll('.add-to-wishlist-btn').forEach(function (btn) {
    btn.addEventListener('click', function (ev) {
      ev.preventDefault();
      const productId = btn.getAttribute('data-product-id');
      if (productId) {
        addToWishlist(parseInt(productId, 10), btn);
      } else {
        showNotification('Please login to add to wishlist', 'warning');
      }
    });
  });

  // Remove from wishlist buttons
  document.querySelectorAll('.remove-from-wishlist-btn').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      const productId = el.getAttribute('data-product-id');
      if (productId && confirm('Remove from wishlist?')) {
        removeFromWishlist(parseInt(productId, 10), el);
      }
    });
  });

  // Add remove from cart functionality if available
  document.querySelectorAll('[data-remove-from-cart]').forEach(function (el) {
    el.addEventListener('click', function (ev) {
      ev.preventDefault();
      const itemId = el.getAttribute('data-remove-from-cart');
      if (itemId && confirm('Remove item from cart?')) {
        removeFromCart(itemId);
      }
    });
  });
});

// CSS for animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(100px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  @keyframes fadeOut {
    from {
      opacity: 1;
    }
    to {
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
