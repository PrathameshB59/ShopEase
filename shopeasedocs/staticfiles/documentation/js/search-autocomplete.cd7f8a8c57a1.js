/**
 * Search Autocomplete for ShopEase Docs
 */
(function() {
    const searchInput = document.getElementById('docs-search-input');
    if (!searchInput) return;

    let dropdown = document.createElement('div');
    dropdown.className = 'search-autocomplete-dropdown';
    dropdown.style.cssText = 'position:absolute;top:100%;left:0;right:0;background:var(--bs-body-bg,#fff);border:1px solid var(--bs-border-color,#dee2e6);border-radius:0.5rem;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:1050;display:none;max-height:400px;overflow-y:auto;';
    searchInput.parentElement.style.position = 'relative';
    searchInput.parentElement.appendChild(dropdown);

    let debounceTimer;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        if (query.length < 2) { dropdown.style.display = 'none'; return; }

        debounceTimer = setTimeout(function() {
            fetch('/ajax/search-suggest/?q=' + encodeURIComponent(query))
                .then(r => r.json())
                .then(data => {
                    if (!data.results || data.results.length === 0) {
                        dropdown.style.display = 'none';
                        return;
                    }
                    dropdown.innerHTML = data.results.map(item =>
                        `<a href="${item.url}" class="d-block px-3 py-2 text-decoration-none border-bottom" style="color:var(--bs-body-color);">
                            <div class="d-flex align-items-center">
                                <i class="bi ${item.icon} me-2 text-muted"></i>
                                <div>
                                    <div class="fw-semibold small">${item.title}</div>
                                    <div class="text-muted" style="font-size:0.75rem">${item.type}</div>
                                </div>
                            </div>
                        </a>`
                    ).join('');
                    dropdown.style.display = 'block';
                })
                .catch(() => { dropdown.style.display = 'none'; });
        }, 300);
    });

    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
})();
