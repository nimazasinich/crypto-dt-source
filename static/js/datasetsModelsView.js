import apiClient from './apiClient.js';

class DatasetsModelsView {
    constructor(section) {
        this.section = section;
        this.datasetsBody = section.querySelector('[data-datasets-body]');
        this.modelsBody = section.querySelector('[data-models-body]');
        this.previewButton = section.querySelector('[data-preview-dataset]');
        this.previewModal = section.querySelector('[data-dataset-modal]');
        this.previewContent = section.querySelector('[data-dataset-modal-content]');
        this.closePreview = section.querySelector('[data-close-dataset-modal]');
        this.modelTestForm = section.querySelector('[data-model-test-form]');
        this.modelTestOutput = section.querySelector('[data-model-test-output]');
        this.datasets = [];
        this.models = [];
    }

    async init() {
        await Promise.all([this.loadDatasets(), this.loadModels()]);
        this.bindEvents();
    }

    bindEvents() {
        if (this.closePreview) {
            this.closePreview.addEventListener('click', () => this.toggleModal(false));
        }
        if (this.previewModal) {
            this.previewModal.addEventListener('click', (event) => {
                if (event.target === this.previewModal) this.toggleModal(false);
            });
        }
        if (this.modelTestForm && this.modelTestOutput) {
            this.modelTestForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                const formData = new FormData(this.modelTestForm);
                this.modelTestOutput.innerHTML = '<p>Sending prompt to model...</p>';
                const result = await apiClient.testModel({
                    model: formData.get('model'),
                    text: formData.get('input'),
                });
                if (!result.ok) {
                    this.modelTestOutput.innerHTML = `<div class="inline-message inline-error">${result.error}</div>`;
                    return;
                }
                this.modelTestOutput.innerHTML = `<pre>${JSON.stringify(result.data, null, 2)}</pre>`;
            });
        }
    }

    async loadDatasets() {
        if (!this.datasetsBody) return;
        const result = await apiClient.getDatasetsList();
        if (!result.ok) {
            this.datasetsBody.innerHTML = `<tr><td colspan="4">${result.error}</td></tr>`;
            return;
        }
        this.datasets = result.data || [];
        this.datasetsBody.innerHTML = this.datasets
            .map(
                (dataset) => `
                <tr>
                    <td>${dataset.name}</td>
                    <td>${dataset.type || '—'}</td>
                    <td>${dataset.updated_at || dataset.last_updated || '—'}</td>
                    <td><button class="ghost" data-dataset="${dataset.name}">Preview</button></td>
                </tr>
            `,
            )
            .join('');
        this.section.querySelectorAll('button[data-dataset]').forEach((button) => {
            button.addEventListener('click', () => this.previewDataset(button.dataset.dataset));
        });
    }

    async previewDataset(name) {
        if (!name) return;
        this.toggleModal(true);
        this.previewContent.innerHTML = `<p>Loading ${name} sample...</p>`;
        const result = await apiClient.getDatasetSample(name);
        if (!result.ok) {
            this.previewContent.innerHTML = `<div class="inline-message inline-error">${result.error}</div>`;
            return;
        }
        const rows = result.data || [];
        if (!rows.length) {
            this.previewContent.innerHTML = '<p>No sample rows available.</p>';
            return;
        }
        const headers = Object.keys(rows[0]);
        this.previewContent.innerHTML = `
            <table>
                <thead><tr>${headers.map((h) => `<th>${h}</th>`).join('')}</tr></thead>
                <tbody>
                    ${rows
                        .map((row) => `<tr>${headers.map((h) => `<td>${row[h]}</td>`).join('')}</tr>`)
                        .join('')}
                </tbody>
            </table>
        `;
    }

    toggleModal(state) {
        if (!this.previewModal) return;
        this.previewModal.classList.toggle('active', state);
    }

    async loadModels() {
        if (!this.modelsBody) return;
        const result = await apiClient.getModelsList();
        if (!result.ok) {
            this.modelsBody.innerHTML = `<tr><td colspan="4">${result.error}</td></tr>`;
            return;
        }
        this.models = result.data || [];
        this.modelsBody.innerHTML = this.models
            .map(
                (model) => `
                <tr>
                    <td>${model.name}</td>
                    <td>${model.task || '—'}</td>
                    <td>${model.status || '—'}</td>
                    <td>${model.description || ''}</td>
                </tr>
            `,
            )
            .join('');
        const modelSelect = this.section.querySelector('[data-model-select]');
        if (modelSelect) {
            modelSelect.innerHTML = this.models.map((m) => `<option value="${m.name}">${m.name}</option>`).join('');
        }
    }
}

export default DatasetsModelsView;
