// cart.js - handles AJAX add/update, selection, totals, and badge

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
const csrftoken = getCookie('csrftoken');

function updateBadge(count){
  const badge = document.getElementById('cart-badge');
  if(!badge) return;
  badge.textContent = count>0?count:'';
}

// Add-to-cart handler
async function addToCartAjax(productId, quantity=1, button=null){
  const resp = await fetch(`/cart/add_ajax/${productId}/`,{method:'POST', headers:{'X-CSRFToken':csrftoken}, body:new URLSearchParams({'quantity': quantity})});
  const data = await resp.json();
  if(data.success){
    updateBadge(data.cart_count);
    if(button){
      // show quick visual feedback
      const orig = button.innerHTML;
      button.innerHTML = 'Added';
      setTimeout(()=> button.innerHTML = orig, 900);
    }
  }
}

// Intercept Add buttons on product list and detail
function setupAddButtons(){
  document.querySelectorAll('[data-add-product]').forEach(btn=>{
    btn.addEventListener('click', async function(e){
      e.preventDefault();
      const pid = this.dataset.addProduct;
      const qtyInput = this.closest('[data-qty-form]')?.querySelector('[data-qty]');
      const qty = qtyInput? Math.max(1, parseInt(qtyInput.value||1)) : 1;
      await addToCartAjax(pid, qty, this);
    });
  });
}

// Cart page functionality
function formatMoney(val){
  return parseFloat(val).toFixed(2);
}

async function updateQty(pid, qty, updateUI=true){
  const body = new URLSearchParams({'pid': pid, 'quantity': qty});
  const resp = await fetch('/cart/update_ajax/', {method:'POST', headers:{'X-CSRFToken':csrftoken}, body});
  if(!resp.ok) return null;
  const data = await resp.json();
  updateBadge(data.cart_count);
  if(updateUI){
    // update item subtotal if present
    const subEl = document.querySelector(`[data-subtotal="${pid}"]`);
    if(subEl && data.item_subtotal!==undefined) subEl.textContent = formatMoney(data.item_subtotal);
    // update global totals if necessary
    const cartTotalEl = document.getElementById('cart-total-all');
    if(cartTotalEl && data.total_amount!==undefined) cartTotalEl.textContent = formatMoney(data.total_amount);
  }
  return data;
}

function computeSelectedTotal(){
  let total = 0;
  document.querySelectorAll('.cart-item-row').forEach(row=>{
    const pid = row.dataset.pid;
    const checked = row.querySelector('.select-item')?.checked;
    if(checked){
      const sub = parseFloat(row.querySelector('[data-subtotal]')?.textContent || 0);
      total += sub;
    }
  });
  const selTotalEl = document.getElementById('cart-selected-total');
  if(selTotalEl) selTotalEl.textContent = formatMoney(total);
  const checkoutBtn = document.getElementById('checkout-btn');
  if(checkoutBtn) checkoutBtn.disabled = total<=0;
  // remove possible warning
  const warning = document.getElementById('checkout-warning');
  if(warning) warning.classList.add('d-none');
}

function setupCartControls(){
  // plus/minus buttons
  document.querySelectorAll('.qty-decrease').forEach(btn=>{
    btn.addEventListener('click', async function(e){
      e.preventDefault();
      const row = this.closest('.cart-item-row');
      const pid = row.dataset.pid;
      const input = row.querySelector('.qty-input');
      let qty = Math.max(1, parseInt(input.value || 1) - 1);
      input.value = qty;
      await updateQty(pid, qty);
      computeSelectedTotal();
    });
  });
  document.querySelectorAll('.qty-increase').forEach(btn=>{
    btn.addEventListener('click', async function(e){
      e.preventDefault();
      const row = this.closest('.cart-item-row');
      const pid = row.dataset.pid;
      const input = row.querySelector('.qty-input');
      let qty = Math.max(1, parseInt(input.value || 1) + 1);
      input.value = qty;
      await updateQty(pid, qty);
      computeSelectedTotal();
    });
  });
  // input manual change
  document.querySelectorAll('.qty-input').forEach(inp=>{
    inp.addEventListener('change', async function(e){
      const row = this.closest('.cart-item-row');
      const pid = row.dataset.pid;
      let qty = Math.max(1, parseInt(this.value || 1));
      this.value = qty;
      await updateQty(pid, qty);
      computeSelectedTotal();
    });
  });
  // selection checkboxes
  document.querySelectorAll('.select-item').forEach(ch=>{
    ch.addEventListener('change', function(){
      computeSelectedTotal();
    });
  });
  // remove item
  document.querySelectorAll('.remove-item').forEach(btn=>{
    btn.addEventListener('click', async function(e){
      e.preventDefault();
      const pid = this.dataset.pid;
      const body = new URLSearchParams({'pid': pid, 'action': 'remove'});
      const resp = await fetch('/cart/update_ajax/', {method:'POST', headers:{'X-CSRFToken':csrftoken}, body});
      const data = await resp.json();
      if(data.success){
        // remove row
        document.querySelector(`.cart-item-row[data-pid="${pid}"]`).remove();
        const cartTotalEl = document.getElementById('cart-total-all');
        if(cartTotalEl && data.total_amount!==undefined) cartTotalEl.textContent = formatMoney(data.total_amount);
        updateBadge(data.cart_count);
        computeSelectedTotal();
      }
    });
  });
  // checkout button
  const checkoutBtn = document.getElementById('checkout-btn');
  if(checkoutBtn){
    checkoutBtn.addEventListener('click', async function(e){
      e.preventDefault();
      const selected = Array.from(document.querySelectorAll('.select-item:checked')).map(ch=>ch.value);
      if(selected.length===0){
        const warning = document.getElementById('checkout-warning');
        if(warning){
          warning.textContent = 'Please select at least one item to checkout.';
          warning.classList.remove('d-none');
        }
        return;
      }
      const body = new URLSearchParams();
      selected.forEach(pid=>body.append('selected', pid));
      const resp = await fetch('/cart/checkout_prepare/', {method:'POST', headers:{'X-CSRFToken':csrftoken}, body});
      const data = await resp.json();
      if(data.success && data.redirect){
        window.location.href = data.redirect;
      } else {
        const warning = document.getElementById('checkout-warning');
        if(warning){
          warning.textContent = 'Unable to prepare checkout. Please try again.';
          warning.classList.remove('d-none');
        }
      }
    });
  }
}

// Initialize UI handlers
document.addEventListener('DOMContentLoaded', function(){
  setupAddButtons();
  setupCartControls();
  computeSelectedTotal();
  // fetch initial summary to populate badge
  fetch('/cart/summary_ajax/').then(r=>r.json()).then(d=>updateBadge(d.cart_count));
});