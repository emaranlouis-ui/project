/**
 * Easy POS - JavaScript Controller
 * Handles: cart state, category filtering, AJAX order submission, invoice printing
 */

/* ---- State ---- */
const cart = {};        // { productId: { name, price, quantity, image } }
let orderCounter = 100; // Local sequence for temp order IDs

/* ---- DOM Refs ---- */
const cartList        = document.getElementById('cart-list');
const lblTotalItems   = document.getElementById('lbl-total-items');
const lblTotalQty     = document.getElementById('lbl-total-quantity');
const lblTotalAmount  = document.getElementById('lbl-total-amount');
const lblOrderId      = document.getElementById('lbl-order-id');
const lblInvoiceNum   = document.getElementById('lbl-invoice-number');
const lblInvoiceDate  = document.getElementById('lbl-invoice-date');
const cartEmptyMsg    = document.querySelector('.cart-empty-msg');
const btnPayments     = document.getElementById('btn-payments');
const btnPrint        = document.getElementById('btn-print-invoice');
const btnNewOrder     = document.getElementById('btn-new-order');
const csrfToken       = document.getElementById('csrf-token').value;

const btnToggleCart      = document.getElementById('btn-toggle-cart');
const btnCloseCartMobile = document.getElementById('btn-close-cart-mobile');
const cartOverlay        = document.getElementById('cart-overlay');
const sidebarRight       = document.querySelector('.pos-sidebar-right');

/* ---- Init ---- */
document.addEventListener('DOMContentLoaded', () => {
    updateInvoiceDate();
    setInterval(updateInvoiceDate, 30000);
    updateOrderCounter();
    bindCategoryFilters();
    bindSubcategoryPills();
    bindProductCards();
    renderCart();
    createToastContainer();

    btnPayments.addEventListener('click', submitOrder);
    btnPrint.addEventListener('click', printInvoice);
    if (btnNewOrder) btnNewOrder.addEventListener('click', clearCart);

    if (btnToggleCart) btnToggleCart.addEventListener('click', toggleMobileCart);
    if (btnCloseCartMobile) btnCloseCartMobile.addEventListener('click', toggleMobileCart);
    if (cartOverlay) cartOverlay.addEventListener('click', toggleMobileCart);
});

function toggleMobileCart() {
    if (sidebarRight) sidebarRight.classList.toggle('open');
    if (cartOverlay) cartOverlay.classList.toggle('active');
}

/* =============================================
   DATE & ORDER COUNTER
   ============================================= */

function updateInvoiceDate() {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const dateStr = `${pad(now.getDate())}/${pad(now.getMonth() + 1)}/${now.getFullYear()} | ${pad(now.getHours())}:${pad(now.getMinutes())}`;
    if (lblInvoiceDate) lblInvoiceDate.textContent = dateStr;
}

function updateOrderCounter() {
    orderCounter++;
    if (lblOrderId) lblOrderId.textContent = `Order: #${String(orderCounter).padStart(4, '0')}`;
    const rnd = Math.floor(Math.random() * 900000) + 100000;
    if (lblInvoiceNum) lblInvoiceNum.innerHTML = `#${rnd}`;
}

/* =============================================
   CATEGORY & PILL FILTERS
   ============================================= */

function bindCategoryFilters() {
    document.querySelectorAll('.category-icon-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.category-icon-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            const category = item.dataset.category;
            filterProducts(category, null);
        });
    });
}

function bindSubcategoryPills() {
    document.querySelectorAll('.pill-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const sub = btn.dataset.sub;
            filterProducts(null, sub);
        });
    });
}

function filterProducts(category, keyword) {
    const cards = document.querySelectorAll('.product-card');
    cards.forEach(card => {
        const cardCat = card.dataset.category || '';
        const cardName = card.dataset.name || '';

        let show = true;

        if (category && category !== 'all') {
            show = cardCat.toLowerCase().includes(category.toLowerCase());
        }

        if (keyword && keyword !== 'all') {
            show = show && (cardName.toLowerCase().includes(keyword.toLowerCase()) || cardCat.toLowerCase().includes(keyword.toLowerCase()));
        }

        card.style.display = show ? '' : 'none';
        if (show) {
            card.style.animation = 'none';
            requestAnimationFrame(() => {
                card.style.animation = '';
            });
        }
    });
}

/* =============================================
   PRODUCT CARDS INTERACTION
   ============================================= */

function bindProductCards() {
    document.querySelectorAll('.btn-add-product').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            const card = btn.closest('.product-card');
            addToCart(card);
        });
    });

    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', () => addToCart(card));
    });
}

function addToCart(card) {
    const id    = card.dataset.id;
    const name  = card.dataset.name;
    const price = parseInt(card.dataset.price, 10);
    const image = card.dataset.image;

    if (cart[id]) {
        cart[id].quantity += 1;
    } else {
        cart[id] = { name, price, quantity: 1, image };
    }

    card.classList.add('selected');
    showToast(`<i class="fa-solid fa-circle-check"></i> <strong>${name}</strong> ajouté au panier`);
    renderCart();
}

/* =============================================
   CART RENDERING
   ============================================= */

function renderCart() {
    const ids = Object.keys(cart).filter(id => cart[id].quantity > 0);

    // Show / hide empty state
    if (ids.length === 0) {
        cartEmptyMsg.classList.add('visible');
        cartList.innerHTML = '';
    } else {
        cartEmptyMsg.classList.remove('visible');
    }

    // Rebuild cart list
    cartList.innerHTML = '';
    let totalItems    = 0;
    let totalQty      = 0;
    let totalAmount   = 0;

    ids.forEach(id => {
        const item  = cart[id];
        const lineTotal = item.price * item.quantity;
        totalItems  += 1;
        totalQty    += item.quantity;
        totalAmount += lineTotal;

        const li = document.createElement('li');
        li.className = 'cart-item';
        li.dataset.id = id;
        li.innerHTML = `
            <img class="cart-item-img" src="${item.image}" alt="${item.name}" loading="lazy">
            <div class="cart-item-details">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price-unit">${formatPrice(item.price)} × ${item.quantity}</div>
            </div>
            <div class="cart-item-right">
                <span class="cart-item-total">${formatPrice(lineTotal)}</span>
                <div class="cart-item-controls">
                    <button class="qty-btn qty-minus" data-id="${id}" title="Diminuer">−</button>
                    <span class="qty-display">${item.quantity}</span>
                    <button class="qty-btn qty-plus" data-id="${id}" title="Augmenter">+</button>
                    <button class="cart-item-delete" data-id="${id}" title="Supprimer">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                </div>
            </div>
        `;
        cartList.appendChild(li);
    });

    // Bind qty/delete buttons
    cartList.querySelectorAll('.qty-minus').forEach(btn => {
        btn.addEventListener('click', () => changeQty(btn.dataset.id, -1));
    });
    cartList.querySelectorAll('.qty-plus').forEach(btn => {
        btn.addEventListener('click', () => changeQty(btn.dataset.id, 1));
    });
    cartList.querySelectorAll('.cart-item-delete').forEach(btn => {
        btn.addEventListener('click', () => removeFromCart(btn.dataset.id));
    });

    // Update summary labels
    lblTotalItems.textContent  = totalItems;
    lblTotalQty.textContent    = totalQty;
    lblTotalAmount.textContent = formatPrice(totalAmount);

    // Update mobile cart FAB labels
    const mobileBadge = document.getElementById('mobile-cart-badge');
    const mobileTotal = document.getElementById('mobile-cart-total');
    if (mobileBadge) mobileBadge.textContent = totalQty;
    if (mobileTotal) mobileTotal.textContent = formatPrice(totalAmount);
}

function changeQty(id, delta) {
    if (!cart[id]) return;
    cart[id].quantity += delta;
    if (cart[id].quantity <= 0) {
        removeFromCart(id);
        return;
    }
    renderCart();
}

function removeFromCart(id) {
    delete cart[id];
    // Deselect product card
    const card = document.querySelector(`.product-card[data-id="${id}"]`);
    if (card) card.classList.remove('selected');
    renderCart();
}

function clearCart() {
    Object.keys(cart).forEach(id => delete cart[id]);
    document.querySelectorAll('.product-card.selected').forEach(c => c.classList.remove('selected'));
    updateOrderCounter();
    renderCart();
}

/* =============================================
   CHECKOUT / SUBMIT ORDER
   ============================================= */

async function submitOrder() {
    const ids = Object.keys(cart).filter(id => cart[id].quantity > 0);
    if (ids.length === 0) {
        showToast('<i class="fa-solid fa-circle-exclamation"></i> Votre panier est vide', 'error');
        return;
    }

    const items = ids.map(id => ({
        product_id: id,
        quantity: cart[id].quantity,
    }));

    const clientSelect  = document.getElementById('select-client');
    const paymentSelect = document.getElementById('select-payment');

    const payload = {
        items,
        client_id: clientSelect.value || null,
        mode_de_paiement: paymentSelect.value,
        type_commande: 'Sur place',
    };

    // Show loading state
    const originalText = btnPayments.innerHTML;
    btnPayments.innerHTML = '<div class="spinner"></div> Traitement...';
    btnPayments.disabled = true;

    try {
        const response = await fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.success) {
            showToast(
                `<i class="fa-solid fa-circle-check"></i> Commande #${data.order_id} enregistrée avec succès !`,
                'success'
            );
            clearCart();
        } else {
            showToast(
                `<i class="fa-solid fa-circle-xmark"></i> Erreur : ${data.error}`,
                'error'
            );
        }
    } catch (err) {
        showToast('<i class="fa-solid fa-circle-xmark"></i> Erreur réseau. Veuillez réessayer.', 'error');
    } finally {
        btnPayments.innerHTML = originalText;
        btnPayments.disabled = false;
    }
}

/* =============================================
   PRINT INVOICE
   ============================================= */

function printInvoice() {
    const ids = Object.keys(cart).filter(id => cart[id].quantity > 0);
    if (ids.length === 0) {
        showToast('<i class="fa-solid fa-circle-exclamation"></i> Le panier est vide', 'error');
        return;
    }

    const invoiceNum = document.getElementById('lbl-invoice-number').textContent;
    const invoiceDate = document.getElementById('lbl-invoice-date').textContent;
    const tableSelect = document.getElementById('select-table');
    const tableLabel  = tableSelect.options[tableSelect.selectedIndex]?.text || 'N/A';
    const total = ids.reduce((sum, id) => sum + cart[id].price * cart[id].quantity, 0);

    const rows = ids.map(id => {
        const item = cart[id];
        return `
            <tr>
                <td>${item.name}</td>
                <td style="text-align:center">${item.quantity}</td>
                <td style="text-align:right">${formatPrice(item.price)}</td>
                <td style="text-align:right">${formatPrice(item.price * item.quantity)}</td>
            </tr>
        `;
    }).join('');

    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ticket de Caisse - EasyPOS</title>
            <style>
                body { font-family: 'Courier New', monospace; font-size: 12px; max-width: 350px; margin: 0 auto; padding: 16px; }
                h1 { font-size: 16px; text-align: center; margin-bottom: 4px; }
                .sub { text-align: center; font-size: 10px; color: #666; margin-bottom: 12px; }
                .divider { border-top: 1px dashed #999; margin: 8px 0; }
                table { width: 100%; border-collapse: collapse; }
                th { text-align: left; border-bottom: 1px solid #333; padding-bottom: 4px; font-size: 10px; }
                td { padding: 4px 0; vertical-align: top; }
                .total-row { font-weight: bold; border-top: 1px solid #333; }
                .footer { text-align: center; font-size: 10px; margin-top: 16px; color: #555; }
            </style>
        </head>
        <body>
            <h1>Easy POS</h1>
            <div class="sub">Restaurant Manager</div>
            <div class="sub">Facture ${invoiceNum} — ${invoiceDate}</div>
            <div class="sub">Table : ${tableLabel}</div>
            <div class="divider"></div>
            <table>
                <thead>
                    <tr>
                        <th>Produit</th>
                        <th style="text-align:center">Qte</th>
                        <th style="text-align:right">P.U.</th>
                        <th style="text-align:right">Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
                <tfoot>
                    <tr class="total-row">
                        <td colspan="3">TOTAL</td>
                        <td style="text-align:right">${formatPrice(total)}</td>
                    </tr>
                </tfoot>
            </table>
            <div class="divider"></div>
            <div class="footer">Merci de votre visite !<br>Conservez ce ticket.</div>
            <script>window.onload = () => { window.print(); window.close(); }<\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

/* =============================================
   TOAST NOTIFICATIONS
   ============================================= */

function createToastContainer() {
    if (!document.querySelector('.toast-container')) {
        const el = document.createElement('div');
        el.className = 'toast-container';
        document.body.appendChild(el);
    }
}

function showToast(message, type = 'default') {
    const container = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast${type !== 'default' ? ` toast-${type}` : ''}`;
    toast.innerHTML = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/* =============================================
   HELPERS
   ============================================= */

function formatPrice(amount) {
    return new Intl.NumberFormat('fr-FR').format(amount) + ' FCFA';
}
