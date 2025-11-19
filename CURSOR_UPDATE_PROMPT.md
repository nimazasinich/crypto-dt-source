### Cursor Agent Prompt – UPDATE ONLY (no rewrite!)

Fix HF models, complete providers/resources, and integrate JSON registries into UI

You are working on an existing project called **Crypto Intelligence Hub** (the `final/` project the user uploaded).

It is already a full FastAPI + HTML/JS dashboard designed to run as a **Hugging Face Docker Space**.

> 🚨 CRITICAL WARNING – THIS IS AN UPDATE, NOT A REWRITE
>
> * Do **NOT** rewrite the architecture.
> * Do **NOT** introduce new frameworks.
> * Do **NOT** delete or replace major modules.
> * Do **NOT** simplify logic by removing features.
>   Your job is to **fix, complete, and wire up** what is already there, and **leverage the new JSON files** the user added.

---

## 1. Existing structure (do not change high-level architecture)

Repository root contains (focus on these, do not move them):

* `final/hf_unified_server.py`

  * ASGI entry point for the Docker Space:

    ```python
    from api_server_extended import app
    ```

* `final/api_server_extended.py`

  * Main FastAPI application:

    * Endpoints:

      * `/api/market`, `/api/trending`, `/api/news`, `/api/sentiment`

      * `/api/providers`, `/api/resources`, `/api/models/*`

      * `/api/diagnostics/*`, `/api/endpoints`, `/api/logs/*`, `/api/pools`

      * `/health`, `/api/status`, etc.

    * SQLite DB at `data/database/crypto_monitor.db`:

      * `prices`

      * `sentiment_analysis`

      * `news_articles`

    * Mounts static files and HTML templates.

    * Defines `WORKSPACE_ROOT` and config paths.

* `final/ai_models.py`

  * Hugging Face model registry and pipeline manager:

    * Uses env: `HF_MODE`, `HF_TOKEN`, etc.

    * Holds `MODEL_SPECS`, logical groups:

      * `CRYPTO_SENTIMENT_MODELS`

      * `FINANCIAL_SENTIMENT_MODELS`

      * `SOCIAL_SENTIMENT_MODELS`

      * `NEWS_SENTIMENT_MODELS`

    * Provides `ModelRegistry`, `initialize_models()`, `get_pipeline()`, `ensemble_crypto_sentiment(...)`, etc.

* `final/config.py`

  * Declares base HF model IDs in `HUGGINGFACE_MODELS`, including:

    * `"crypto_sentiment": "ElKulako/cryptobert"`

    * `"sentiment_financial": "ProsusAI/finbert"`

    * Other sentiment/summarization models.

* `final/templates/index.html`

* `final/templates/unified_dashboard.html`

  * Main "Ultimate" dashboard HTML:

    * Tabs: Market, Monitor, Admin, HF, Pools, Logs, Resources, Reports, Advanced.

    * Dark/glass style visual layout.

* `final/static/js/app.js`

  * Main front-end logic:

    * Tab switching: `switchTab`, `loadTabData`.

    * Data loaders: `loadMarketData`, `loadModels`, `loadSentimentModels`, `loadSentimentHistory`, `loadNews`, `loadProviders`, `loadDiagnostics`, `loadAPIEndpoints`, etc.

    * Calls backend endpoints under `/api/...`.

* `final/static/css/main.css`

  * Main CSS for dashboard styling.

* `final/api-resources/`

  * Contains JSON resource files (but some code paths still expect other JSON names/locations).

You must work within this architecture. Do not introduce React/Vue, do not move to a new server entry, etc.

---

## 2. New JSON files that MUST be used

The user has added **three important JSON files** that you must integrate into the backend and UI:

1. `providers_config_extended.json`

   * Extended registry of providers (CoinGecko, CoinPaprika, explorers, DeFi, etc.).

   * Contains detailed metadata: `category`, `base_url`, `endpoints`, `rate_limit`, `requires_auth`, `priority`, `weight`, etc.

2. `PROVIDER_AUTO_DISCOVERY_REPORT.json`

   * Auto-discovery validation report:

   * Contains:

     * `stats`: counts of HTTP/HF providers, valid/invalid/conditional, execution time, etc.

     * `http_providers.results[]`: each with:

       * `provider_id`, `provider_name`, `provider_type`, `category`

       * `status` (`VALID`, `INVALID`, `CONDITIONALLY_AVAILABLE`)

       * `requires_auth`, `auth_env_var`, `error_reason`, `test_endpoint`, `response_time_ms`, `response_sample`.

   * This is a **runtime validation snapshot** that must be exposed in the UI (e.g., as a diagnostics/providers health section).

3. `all_apis_merged_2025.json`

   * Master registry of APIs and keys:

     * `metadata`: name, version (`2025.11.11`), description, created_at, source_files.

     * `raw_files[]`: with big config text, free CORS proxies, RPC nodes, explorers, market data APIs, etc.

   * This should back **API Explorer / Resources UI**, showing:

     * Categories (market data, explorers, RPC, etc.).

     * Example endpoints and usage.

     * Possibly mention of CORS proxy patterns.

> You must **explicitly use these three files** in backend endpoints and update the UI to surface this information in a structured, useful way.

---

## 3. Known problems you must fix (without rewriting)

### 3.1 HF models: 401, invalid IDs, 0 loaded pipelines

Logs show:

* For `ElKulako/cryptobert` and `ProsusAI/finbert`:

  * 401 / Repository Not Found.

  * Expired user access token `DreammakerCryptoSignalAndTrader2`.

* Registry ends up with:

  ```text
  'models_loaded': 0, 'failed': [...]
  ```

But `HF_MODE` gets reported as `'public'` or `'partial'`.

Problem:

* Some configured models are private/gated/not accessible with current token.

* Token is expired.

* The registry says "partial/public" but in practice, **no usable pipelines** exist.

### 3.2 Providers config path & resources mismatch

In `api_server_extended.py`:

```python
PROVIDERS_CONFIG_PATH = WORKSPACE_ROOT / "providers_config_extended.json"
```

Previously, this file did not exist in the project – causing `/api/providers` to return an empty/minimal list.

Also, resources endpoints reference JSON filenames like:

* `crypto_resources_unified_2025-11-11.json`

* `all_apis_merged_2025.json` (or similar)

But the actual files and paths in the `final/` project were not aligned.

### 3.3 Placeholders and half-implemented endpoints

* `/api/pools` returns a static empty list + "not yet implemented" message.

* Some diagnostics endpoints are present but not fully wired to UI.

### 3.4 HTML tabs vs JS logic mismatch

`static/js/app.js` expects tab IDs like:

```js
'dashboard', 'market', 'models', 'sentiment', 'news', 'providers', 'diagnostics', 'api-explorer'
```

But `templates/index.html` / `unified_dashboard.html` defines tabs like:

```html
'market', 'monitor', 'admin', 'hf', 'pools', 'logs', 'resources', 'reports', 'advanced'
```

Thus:

* Tabs such as `'hf'`, `'pools'`, `'logs'`, `'resources'`, `'reports'`, `'advanced'` have **no corresponding JS case**.

* Tabs such as `'models'`, `'sentiment'`, `'diagnostics'`, `'api-explorer'` exist in JS but **not in HTML**.

Result: Many features (models UI, providers UI, diagnostics UI, API explorer) are effectively invisible or non-functional.

### 3.5 Sentiment UI ID/function mismatch

HTML:

* Uses `id="sentimentInput"`, `id="sentimentResult"`, `id="sentimentDetails"`.

* Button calls `onclick="runSentiment()"`.

JS:

* Expects `id="sentiment-text"`, `id="sentiment-mode"`, `id="sentiment-model"`, `id="sentiment-result"`.

* Main handler is `analyzeSentiment()`.

Result: clicking the button throws `runSentiment is not defined`, and DOM IDs do not align.

### 3.6 Missing containers for models/providers/diagnostics/API explorer

* `app.js` renders into elements like `#models-list`, `#models-status`, `#providers-list`, `#api-endpoint-list`, etc.

* These IDs are not present in `index.html`, or are named differently.

Result: even if backend endpoints work, UI has nowhere to render them.

---

## 4. Tasks – with explicit use of the new JSON files

### 4.1 Backend – HF models & registry hardening (ai_models.py, config.py, api_server_extended.py)

* Keep the **existing structure and logic**, but:

1. Implement robust auth and fallback:

   * Respect `HF_MODE` (`off`, `public`, `auth`).

   * In `"public"` mode:

     * Do not rely on any expired or invalid token.

     * Call `transformers.pipeline(...)` without `use_auth_token` or with a safe fallback.

   * In `"auth"` mode:

     * Use `HF_TOKEN` from env if present.

     * If token is missing/invalid, log a concise warning, mark those models as failed, but do **not** crash startup.

2. Per-task fallback chain:

   * For each logical category:

     * Crypto sentiment (`CRYPTO_SENTIMENT_MODELS`).

     * Financial sentiment (`FINANCIAL_SENTIMENT_MODELS`).

     * Social sentiment, news sentiment, summarization, etc.

   * Define an ordered list of **public, reliable** model candidates.

   * `initialize_models()` and `get_pipeline()` should try candidates in order and pick the first that loads.

   * If all candidates in the chain fail:

     * Register a clear `failed` entry in registry.

     * Expose this failure cleanly via `/api/models/status` and `/api/models/list`.

3. Registry & endpoints:

   * `/api/models/status` should return:

     * `status`: `"ok"`, `"partial"`, or `"disabled"`.

     * `hf_mode`, `models_loaded`, `failed` with concise messages.

   * `/api/models/list` should list **logical tasks** (e.g., `crypto_sent_0`, `financial_sent_0`) and indicate:

     * Whether each is loaded.

     * Underlying model ID.

     * Any note (e.g., "requires HF auth", "fallback used").

4. Make sure sentiment endpoints:

   * `/api/sentiment/analyze`

   * `/api/hf/run-sentiment`

   * Any ensemble endpoints

   correctly use the `ModelRegistry` and handle "no available model for this task" without crashing, returning a structured error to the UI.

> Do NOT delete existing task groups or endpoints – only strengthen and complete them.

---

### 4.2 Backend – integrate `providers_config_extended.json`

You **must** integrate this file as the primary providers registry.

1. Locate `providers_config_extended.json` in the repo.

   * If not already under `final/`, move or reference it there.

   * Recommended path: `final/providers_config_extended.json`.

2. In `api_server_extended.py`:

   * Confirm or set:

     ```python
     PROVIDERS_CONFIG_PATH = WORKSPACE_ROOT / "providers_config_extended.json"
     ```

   * Fix `load_providers_config()` to:

     * Load this JSON file.

     * Validate that `config["providers"]` exists and is a dict.

     * Return structured provider data.

3. Update `/api/providers`:

   * Use `providers_config_extended.json` to return a list of providers with fields like:

     * `id` (key).

     * `name`.

     * `category`.

     * `base_url`.

     * `priority`.

     * `weight`.

     * `requires_auth`.

     * `rate_limit`.

   * Optionally include a computed `status` if you correlate with the auto-discovery report (see 4.3).

4. Make sure `/api/providers` is **non-empty** and reflects the JSON content.

---

### 4.3 Backend – integrate `PROVIDER_AUTO_DISCOVERY_REPORT.json`

You must expose the auto-discovery report as part of the diagnostics / providers health.

1. Choose a path, e.g.:

   ```python
   AUTO_DISCOVERY_REPORT_PATH = WORKSPACE_ROOT / "PROVIDER_AUTO_DISCOVERY_REPORT.json"
   ```

2. Add or update endpoint(s) in `api_server_extended.py`, for example:

   * `GET /api/providers/auto-discovery-report`:

     * Returns the parsed JSON from `PROVIDER_AUTO_DISCOVERY_REPORT.json` (or a structured subset).

   * Optionally `GET /api/providers/health-summary`:

     * Returns a simplified summary:

       * `total_active_providers`, `http_valid`, `http_invalid`, `hf_valid`, etc.

       * Aggregated counts by `status` (`VALID`, `INVALID`, `CONDITIONALLY_AVAILABLE`).

3. Optionally link provider configs to the discovery report:

   * When constructing `/api/providers` output:

     * If a provider ID from `providers_config_extended.json` appears in `http_providers.results[]`, merge:

       * `status`, `requires_auth`, `error_reason`, `test_endpoint`, `response_time_ms`.

4. Ensure these endpoints are resilient:

   * If file is missing, return a clear error with `"ok": false`, `"error": "report file not found"`.

   * If JSON parse fails, return an error message instead of raising.

---

### 4.4 Backend – integrate `all_apis_merged_2025.json` as a resources/API explorer source

You must wire this file to the **resources/API explorer** endpoints.

1. Place or reference `all_apis_merged_2025.json` under `final/`, e.g.:

   ```python
   API_REGISTRY_PATH = WORKSPACE_ROOT / "all_apis_merged_2025.json"
   ```

2. In `api_server_extended.py`, create or update endpoints such as:

   * `GET /api/resources/apis`:

     * Returns:

       * `metadata` from the JSON (`name`, `version`, `description`, `created_at`).

       * High-level categories extracted from the text and structure (market data, explorers, RPC nodes, CORS proxies, etc.).

   * `GET /api/resources/apis/raw`:

     * Returns a trimmed version of `raw_files[]` (filename + first N characters) to avoid huge payloads.

   * If you already have `/api/resources`, consider merging:

     * Existing resources.

     * The structured info from this registry into a single consolidated response.

3. You do **not** need to fully parse all free-form text; focus on:

   * Surfacing metadata.

   * Providing an overview of categories.

   * Exposing some example endpoints and usage hints to the UI.

---

### 4.5 Frontend – align tabs and use the new backend endpoints

In `templates/index.html` and `static/js/app.js`:

1. **Synchronize tab IDs** between HTML and JS:

   * For each visible tab button, make sure `switchTab('...')` uses a `tabId` that `loadTabData` recognizes.

   Example mapping (you can refine but it must be consistent):

   * `market` → `loadMarketData()`.

   * `hf` → `loadModels()` + HF diagnostics (models status, HF mode).

   * `resources` → call a new `loadResources()` that fetches `/api/resources/apis` and/or `/api/resources`.

   * `logs` / `advanced` → call `loadDiagnostics()` and `loadAPIEndpoints()`.

2. Either:

   * Update `loadTabData` to handle `'hf'`, `'resources'`, `'logs'`, `'reports'`, `'advanced'`, `'monitor'`, `'admin'`.

   **OR**

   * Change HTML to use IDs that JS already expects (`models`, `providers`, `diagnostics`, `api-explorer`).

   **But in any case, every tab shown in HTML must have a corresponding case in JS.**

3. After this change:

   * Clicking each tab must trigger at least one data-loading function and update UI.

---

### 4.6 Frontend – sentiment UI fix (and usage of models)

You must make the sentiment panel fully functional using the backend models.

1. In HTML (`index.html`):

   * Decide on final IDs and stick to them. For example:

     ```html
     <textarea id="sentiment-text"></textarea>
     <select id="sentiment-mode">...</select>
     <select id="sentiment-model">...</select>
     <button onclick="analyzeSentiment()">Analyze Sentiment</button>
     <div id="sentiment-result"></div>
     <pre id="sentiment-details"></pre>
     ```

   * Or adapt JS to current IDs – just ensure both HTML and JS match.

2. In `app.js`:

   * Implement `analyzeSentiment()` (or `runSentiment()` that calls it) to:

     * Read user input from the sentiment textarea and selectors.

     * POST to the appropriate endpoint:

       * `/api/sentiment/analyze` or `/api/hf/run-sentiment`.

     * Render:

       * A high-level label: positive/negative/neutral.

       * Score/confidence.

       * Any additional metadata.

   * Use the **model registry** endpoints (e.g., `/api/models/list`) to populate the `sentiment-model` select with available sentiment models.

3. Make sure:

   * If no models are available for the chosen task, show a clear warning in the UI rather than crashing.

---

### 4.7 Frontend – providers & auto-discovery UI (using the new JSON-driven endpoints)

You must build UI that actually visualizes:

* Providers from `providers_config_extended.json` (via `/api/providers`).

* Auto-discovery status from `PROVIDER_AUTO_DISCOVERY_REPORT.json` (via new endpoints from section 4.3).

1. In HTML (probably under **HF** or **Resources** or a dedicated **Providers** section):

   * Add containers like:

     ```html
     <div id="providers-panel">
       <div id="providers-summary"></div>
       <table id="providers-list">...</table>
     </div>

     <div id="providers-health-panel">
       <div id="providers-health-summary"></div>
       <table id="providers-health-table">...</table>
     </div>
     ```

2. In `app.js`:

   * Implement or update `loadProviders()` to:

     * Call `/api/providers` and render:

       * Name, category, base_url, requires_auth, priority/weight.

     * Call `/api/providers/auto-discovery-report` (or the endpoint you defined) and render:

       * Total valid/invalid/conditional.

       * A table listing provider_id, status, requires_auth, response_time_ms, error_reason, etc.

3. Use simple but clear CSS from `main.css` to style the tables with:

   * Status badges (`VALID` / `INVALID` / `CONDITIONALLY_AVAILABLE` with distinct styles).

   * Highlight providers that are both present in config and validated successfully.

---

### 4.8 Frontend – API Explorer & Resources UI using `all_apis_merged_2025.json`

Under a suitable tab (e.g. **Resources**, **Advanced**, or a specific **API Explorer** tab):

1. In HTML:

   * Add containers like:

     ```html
     <section id="api-registry-section">
       <div id="api-registry-metadata"></div>
       <div id="api-registry-categories"></div>
       <div id="api-registry-examples"></div>
     </section>
     ```

2. In `app.js`:

   * Implement `loadAPIRegistry()` or reuse `loadAPIEndpoints()` by extending it:

     * Fetch `/api/resources/apis` (or `/api/resources` if merged) to get:

       * `metadata` (name, version, description).

       * High-level category descriptors.

     * Render:

       * Title & version.

       * A list of main categories (market data, explorers, RPC, CORS proxy, etc).

       * A small sample of example endpoints and usage patterns from `all_apis_merged_2025.json`.

3. Optionally:

   * Provide a small search/filter box to filter endpoints by keyword.

   * Provide a "copy example URL" button.

---

### 4.9 CSS – keep style, polish where needed

In `static/css/main.css`:

* Without changing the design language, ensure:

  * Newly-added panels (Providers, Auto-discovery, API Registry) have proper spacing, typography, and responsive behavior.

  * Status labels for providers use distinct colors/icons.

  * Loading and error states are visually clear (e.g., `.loading`, `.error-message` styles).

Do not introduce new libraries; just extend existing CSS.

---

## 5. Constraints & style rules

* Work **only** within:

  * `final/api_server_extended.py`

  * `final/ai_models.py`

  * `final/config.py` (only small, safe updates)

  * `final/templates/index.html` (and `unified_dashboard.html` if shared)

  * `final/static/js/app.js`

  * `final/static/css/main.css`

  * Plus minor additions to wire in the three JSON files.

* Do **NOT**:

  * Delete or move `hf_unified_server.py`, `api_server_extended.py`, or `app.py`.

  * Introduce new frameworks (no React/Vue).

  * Replace the HTML with a completely new page.

  * Remove existing endpoints or DB tables.

* Do:

  * Use the three JSON files as **authoritative data sources**:

    * `providers_config_extended.json` for `/api/providers`.

    * `PROVIDER_AUTO_DISCOVERY_REPORT.json` for providers diagnostics.

    * `all_apis_merged_2025.json` for API explorer/resources.

  * Keep HF model logic, but harden and complete it.

  * Make all UI tabs functional and wired to their backend endpoints.

  * Ensure the models that are pipelined are actually used in the sentiment and AI-related UI.

---

## 6. Acceptance criteria

1. HF models & registry:

   * Server boots without unhandled exceptions, even if some models are unavailable/private.

   * At least one sentiment model is loaded in `"public"` mode if public models are accessible.

   * `/api/models/status` and `/api/models/list` correctly reflect loaded and failed models.

2. Providers & resources:

   * `/api/providers` returns a list based on `providers_config_extended.json`.

   * Auto-discovery endpoints expose data from `PROVIDER_AUTO_DISCOVERY_REPORT.json`.

   * `/api/resources/apis` (or equivalent) uses `all_apis_merged_2025.json`.

3. UI:

   * All visible tabs call appropriate JS loaders and show content.

   * Sentiment panel works end-to-end:

     * User enters text → backend analyzes → UI shows label & score.

   * HF/models tab shows model status and availability.

   * Providers tab shows:

     * Config providers list (name, category, base_url, auth requirement).

     * Auto-discovery health summary & per-provider status.

   * Resources/API explorer tab shows metadata + example APIs from `all_apis_merged_2025.json`.

4. No regressions:

   * Market/price charts still work.

   * No new JS errors appear in normal user flows.

Once all of the above are satisfied, stop.

