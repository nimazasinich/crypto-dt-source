export function formatCurrency(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return '—';
    }
    const num = Number(value);
    if (Math.abs(num) >= 1_000_000_000_000) {
        return `$${(num / 1_000_000_000_000).toFixed(2)}T`;
    }
    if (Math.abs(num) >= 1_000_000_000) {
        return `$${(num / 1_000_000_000).toFixed(2)}B`;
    }
    if (Math.abs(num) >= 1_000_000) {
        return `$${(num / 1_000_000).toFixed(2)}M`;
    }
    return `$${num.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

export function formatPercent(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) {
        return '—';
    }
    const num = Number(value);
    return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
}

export function setBadge(element, value) {
    if (!element) return;
    element.textContent = value;
}

export function renderMessage(container, { state, title, body }) {
    if (!container) return;
    container.innerHTML = `
        <div class="inline-message inline-${state}">
            <strong>${title}</strong>
            <p>${body}</p>
        </div>
    `;
}

export function createSkeletonRows(count = 3, columns = 5) {
    let rows = '';
    for (let i = 0; i < count; i += 1) {
        rows += '<tr class="skeleton">';
        for (let j = 0; j < columns; j += 1) {
            rows += '<td><span class="skeleton-block"></span></td>';
        }
        rows += '</tr>';
    }
    return rows;
}

export function toggleSection(section, active) {
    if (!section) return;
    section.classList.toggle('active', !!active);
}

export function shimmerElements(container) {
    if (!container) return;
    container.querySelectorAll('[data-shimmer]').forEach((el) => {
        el.classList.add('shimmer');
    });
}
