var cart = [];
var product = { id: 1, name: 'WAFFLE LONG SLEEVE', price: 4399 };
function toggleMenu() {
  var m = document.getElementById('mobileMenu');
  if (m) m.classList.toggle('open');
}
function addToCart(id) {
  var sizeVal = 'ONE';
  var found = null;
  for (var i = 0; i < cart.length; i++) { if (cart[i].id === id) { found = cart[i]; break; } }
  if (found) { found.qty++; } else { cart.push({ id: id, size: sizeVal, qty: 1, name: product.name, price: product.price }); }
  updateCart();
  showNotification('Added to cart');
}
function removeFromCart(idx) { cart.splice(idx, 1); updateCart(); }
function updateCart() {
  var count = 0;
  for (var i = 0; i < cart.length; i++) count += cart[i].qty;
  document.getElementById('cart-count').textContent = count;
  var e = document.getElementById('cartEmpty');
  var c = document.getElementById('cartContent');
  if (count === 0) { e.classList.remove('hidden'); c.classList.add('hidden'); }
  else { e.classList.add('hidden'); c.classList.remove('hidden'); renderCart(); }
}
function renderCart() {
  var div = document.getElementById('cartItems');
  var html = '';
  var t = 0;
  for (var i = 0; i < cart.length; i++) {
    var it = cart[i];
    html += '<div class="cart-item"><div class="cart-item-info"><h4>' + it.name + '</h4><p>ONE SIZE x ' + it.qty + '</p></div><div class="cart-item-price">' + (it.price * it.qty).toLocaleString() + ' RUB</div><button class="cart-item-remove" onclick="removeFromCart(' + i + ')">x</button></div>';
    t += it.price * it.qty;
  }
  div.innerHTML = html;
  document.getElementById('cartTotal').textContent = t.toLocaleString() + ' RUB';
}
function checkout() {
  var t = 0, c = 0;
  for (var i = 0; i < cart.length; i++) { c += cart[i].qty; t += cart[i].price * cart[i].qty; }
  alert('MOCK CHECKOUT\n\nTest mode.\n\nItems: ' + c + '\nTotal: ' + t.toLocaleString() + ' RUB');
}
function showNotification(msg) {
  var n = document.createElement('div');
  n.textContent = msg;
  n.style.cssText = 'position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:#fff;color:#000;padding:12px 30px;font-size:12px;letter-spacing:1px;font-weight:600;z-index:9999';
  document.body.appendChild(n);
  setTimeout(function() { n.style.opacity = '0'; setTimeout(function() { n.remove(); }, 400); }, 2000);
}
document.addEventListener('mousemove', function(e) {
  var f = document.querySelector('.cursor-follower');
  if (f) { f.style.left = e.clientX + 'px'; f.style.top = e.clientY + 'px'; }
});
updateCart();