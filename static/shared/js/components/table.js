/**
 * Enhanced Table Component
 * Features:
 * - Sortable columns
 * - Filterable data
 * - Pagination
 * - Responsive design
 * - Loading states
 * - Empty states
 */

export class EnhancedTable {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = {
      columns: options.columns || [],
      data: options.data || [],
      sortable: options.sortable !== false,
      filterable: options.filterable !== false,
      paginated: options.paginated !== false,
      pageSize: options.pageSize || 10,
      emptyMessage: options.emptyMessage || 'No data available',
      onRowClick: options.onRowClick || null,
      ...options
    };
    
    this.currentPage = 1;
    this.sortColumn = null;
    this.sortDirection = 'asc';
    this.filterQuery = '';
    this.filteredData = [];
    
    this.init();
  }

  /**
   * Initialize table
   */
  init() {
    if (!this.container) {
      console.error('[EnhancedTable] Container not found');
      return;
    }
    
    this.filterData();
    this.render();
  }

  /**
   * Set data
   */
  setData(data) {
    this.options.data = data || [];
    this.currentPage = 1;
    this.filterData();
    this.render();
  }

  /**
   * Filter data based on query
   */
  filterData() {
    if (!this.filterQuery) {
      this.filteredData = [...this.options.data];
    } else {
      const query = this.filterQuery.toLowerCase();
      this.filteredData = this.options.data.filter(row => {
        return this.options.columns.some(col => {
          const value = this.getCellValue(row, col.field);
          return String(value).toLowerCase().includes(query);
        });
      });
    }
    
    // Apply sorting
    if (this.sortColumn) {
      this.applySorting();
    }
  }

  /**
   * Apply sorting
   */
  applySorting() {
    const column = this.options.columns.find(col => col.field === this.sortColumn);
    if (!column) return;
    
    this.filteredData.sort((a, b) => {
      const aVal = this.getCellValue(a, this.sortColumn);
      const bVal = this.getCellValue(b, this.sortColumn);
      
      let comparison = 0;
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else {
        comparison = String(aVal).localeCompare(String(bVal));
      }
      
      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
  }

  /**
   * Get cell value from row
   */
  getCellValue(row, field) {
    if (typeof field === 'function') {
      return field(row);
    }
    return row[field];
  }

  /**
   * Render table
   */
  render() {
    if (!this.container) return;
    
    const html = `
      ${this.options.filterable ? this.renderFilterBar() : ''}
      <div class="table-wrapper">
        ${this.filteredData.length === 0 ? this.renderEmpty() : this.renderTable()}
      </div>
      ${this.options.paginated ? this.renderPagination() : ''}
    `;
    
    this.container.innerHTML = html;
    this.attachEventListeners();
  }

  /**
   * Render filter bar
   */
  renderFilterBar() {
    return `
      <div class="table-filter-bar">
        <div class="search-wrapper">
          <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input 
            type="text" 
            class="table-search-input" 
            placeholder="Search..." 
            value="${this.filterQuery}"
            data-action="filter"
          >
        </div>
        <div class="table-info">
          Showing ${this.filteredData.length} of ${this.options.data.length} items
        </div>
      </div>
    `;
  }

  /**
   * Render table
   */
  renderTable() {
    const start = (this.currentPage - 1) * this.options.pageSize;
    const end = this.options.paginated ? start + this.options.pageSize : this.filteredData.length;
    const pageData = this.filteredData.slice(start, end);
    
    return `
      <table class="enhanced-table">
        <thead>
          <tr>
            ${this.options.columns.map(col => this.renderHeaderCell(col)).join('')}
          </tr>
        </thead>
        <tbody>
          ${pageData.map((row, index) => this.renderRow(row, start + index)).join('')}
        </tbody>
      </table>
    `;
  }

  /**
   * Render header cell
   */
  renderHeaderCell(column) {
    const sortable = this.options.sortable && column.sortable !== false;
    const isSorted = this.sortColumn === column.field;
    const sortIcon = isSorted 
      ? (this.sortDirection === 'asc' ? '↑' : '↓')
      : '';
    
    return `
      <th 
        class="${sortable ? 'sortable' : ''} ${isSorted ? 'sorted' : ''}"
        data-field="${column.field}"
        data-action="${sortable ? 'sort' : ''}"
        style="${column.width ? `width: ${column.width}` : ''}"
      >
        <div class="th-content">
          <span>${column.label}</span>
          ${sortable ? `<span class="sort-icon">${sortIcon}</span>` : ''}
        </div>
      </th>
    `;
  }

  /**
   * Render row
   */
  renderRow(row, index) {
    const clickable = this.options.onRowClick ? 'clickable' : '';
    
    return `
      <tr class="${clickable}" data-index="${index}" data-action="${this.options.onRowClick ? 'row-click' : ''}">
        ${this.options.columns.map(col => this.renderCell(row, col)).join('')}
      </tr>
    `;
  }

  /**
   * Render cell
   */
  renderCell(row, column) {
    const value = this.getCellValue(row, column.field);
    const formatted = column.formatter ? column.formatter(value, row) : value;
    
    return `
      <td class="${column.className || ''}">
        ${formatted}
      </td>
    `;
  }

  /**
   * Render empty state
   */
  renderEmpty() {
    return `
      <div class="table-empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-message">${this.options.emptyMessage}</div>
      </div>
    `;
  }

  /**
   * Render pagination
   */
  renderPagination() {
    const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
    
    if (totalPages <= 1) return '';
    
    const pages = this.getPaginationPages(totalPages);
    
    return `
      <div class="table-pagination">
        <button 
          class="pagination-btn" 
          data-action="prev-page"
          ${this.currentPage === 1 ? 'disabled' : ''}
        >
          ← Previous
        </button>
        
        <div class="pagination-pages">
          ${pages.map(page => {
            if (page === '...') {
              return '<span class="pagination-ellipsis">...</span>';
            }
            return `
              <button 
                class="pagination-page ${page === this.currentPage ? 'active' : ''}"
                data-action="goto-page"
                data-page="${page}"
              >
                ${page}
              </button>
            `;
          }).join('')}
        </div>
        
        <button 
          class="pagination-btn" 
          data-action="next-page"
          ${this.currentPage === totalPages ? 'disabled' : ''}
        >
          Next →
        </button>
      </div>
    `;
  }

  /**
   * Get pagination pages to display
   */
  getPaginationPages(totalPages) {
    const delta = 2;
    const pages = [];
    
    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        (i >= this.currentPage - delta && i <= this.currentPage + delta)
      ) {
        pages.push(i);
      } else if (pages[pages.length - 1] !== '...') {
        pages.push('...');
      }
    }
    
    return pages;
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    this.container.addEventListener('click', (e) => {
      const action = e.target.closest('[data-action]')?.dataset.action;
      
      if (action === 'sort') {
        this.handleSort(e);
      } else if (action === 'prev-page') {
        this.handlePrevPage();
      } else if (action === 'next-page') {
        this.handleNextPage();
      } else if (action === 'goto-page') {
        this.handleGotoPage(e);
      } else if (action === 'row-click') {
        this.handleRowClick(e);
      }
    });
    
    this.container.addEventListener('input', (e) => {
      if (e.target.dataset.action === 'filter') {
        this.handleFilter(e);
      }
    });
  }

  /**
   * Handle sort
   */
  handleSort(e) {
    const th = e.target.closest('th');
    const field = th.dataset.field;
    
    if (this.sortColumn === field) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = field;
      this.sortDirection = 'asc';
    }
    
    this.filterData();
    this.render();
  }

  /**
   * Handle filter
   */
  handleFilter(e) {
    this.filterQuery = e.target.value;
    this.currentPage = 1;
    this.filterData();
    this.render();
  }

  /**
   * Handle previous page
   */
  handlePrevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.render();
    }
  }

  /**
   * Handle next page
   */
  handleNextPage() {
    const totalPages = Math.ceil(this.filteredData.length / this.options.pageSize);
    if (this.currentPage < totalPages) {
      this.currentPage++;
      this.render();
    }
  }

  /**
   * Handle goto page
   */
  handleGotoPage(e) {
    const page = parseInt(e.target.dataset.page);
    if (page && page !== this.currentPage) {
      this.currentPage = page;
      this.render();
    }
  }

  /**
   * Handle row click
   */
  handleRowClick(e) {
    const row = e.target.closest('tr');
    const index = parseInt(row.dataset.index);
    const data = this.filteredData[index];
    
    if (this.options.onRowClick && data) {
      this.options.onRowClick(data, index);
    }
  }

  /**
   * Destroy table
   */
  destroy() {
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

export default EnhancedTable;
