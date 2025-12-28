fetch("../frontend/header.html")
  .then(res => res.text())
  .then(html => {
    document.getElementById("headerContainer").innerHTML = html;
    initHeader();
  });

// --- Cookie helpers ---
function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
}

function getCookie(name) {
    return document.cookie.split('; ').reduce((r, v) => {
        const parts = v.split('=');
        return parts[0] === name ? decodeURIComponent(parts[1]) : r
    }, '');
}

function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=0; path=/';
}

// --- Header logic ---
function initHeader() {
  const userId = getCookie("user_id");
  const loginLink = document.getElementById("loginLink");
  const nav = document.getElementById("mainNav");

  if (!loginLink || !nav) {
    console.warn("Header elements not found");
    return;
  }

  if (userId) {
    loginLink.textContent = "Logga ut";
    loginLink.href = "#";
    loginLink.onclick = (e) => {
      e.preventDefault();
      deleteCookie("user_id");
      window.location.href = "/";
    };

    if (!nav.querySelector('a[href="/mina_sidor"]')) {
      const myPagesLink = document.createElement("a");
      myPagesLink.href = "/mina_sidor";
      myPagesLink.textContent = "Mina sidor";
      nav.insertBefore(myPagesLink, loginLink);
    }
  } else {
    loginLink.textContent = "Logga in";
    loginLink.href = "/login";
  }

  // Standard navigation
  nav.querySelectorAll(".nav-link").forEach(link => {
    link.onclick = (e) => {
      e.preventDefault();
      const target = link.dataset.target;
      if (target) window.location.href = target;
    };
  });
}