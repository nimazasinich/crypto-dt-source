"""
Generate comprehensive test reports in JSON and HTML formats.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List
from dataclasses import asdict
from .browser_utils import TestResult


class ReportGenerator:
    """
    Generates comprehensive test reports with beautiful HTML output.
    """
    
    def __init__(self, results: List[TestResult], config):
        """
        Initialize report generator.
        
        Args:
            results: List of test results
            config: TestConfig object
        """
        self.results = results
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create reports directory
        self.reports_dir = Path("test-results/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def get_summary(self) -> dict:
        """Get test summary statistics"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == 'passed')
        failed = sum(1 for r in self.results if r.status == 'failed')
        skipped = sum(1 for r in self.results if r.status == 'skipped')
        
        total_duration = sum(r.duration for r in self.results)
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'total_duration': total_duration
        }
    
    def result_to_dict(self, result: TestResult) -> dict:
        """Convert TestResult to dictionary"""
        return asdict(result)
    
    def generate_json_report(self):
        """Generate JSON report"""
        summary = self.get_summary()
        
        report = {
            "test_date": datetime.now().isoformat(),
            "environment": self.config.environment,
            "base_url": self.config.base_url,
            "websocket_enabled": self.config.websocket_enabled,
            "summary": summary,
            "results": [self.result_to_dict(r) for r in self.results]
        }
        
        output_path = self.reports_dir / f"report_{self.timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Create symlink to latest
        latest_path = self.reports_dir / "latest.json"
        if latest_path.exists():
            latest_path.unlink()
        
        try:
            latest_path.symlink_to(output_path.name)
        except:
            # Symlinks may not work on Windows, copy instead
            import shutil
            shutil.copy(output_path, latest_path)
        
        print(f"📄 JSON Report: {output_path}")
        return output_path
    
    def generate_html_report(self):
        """Generate beautiful HTML report"""
        summary = self.get_summary()
        
        # Group results by page/category
        page_results = {}
        api_results = []
        ws_results = []
        
        for result in self.results:
            if result.test_name.startswith('API'):
                api_results.append(result)
            elif result.test_name.startswith('WebSocket'):
                ws_results.append(result)
            else:
                # Extract page name from test name
                page = "General"
                if "Navigate to" in result.test_name:
                    page = result.test_name.split("Navigate to")[1].strip()
                
                if page not in page_results:
                    page_results[page] = []
                page_results[page].append(result)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {self.timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; font-size: 0.9em; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{ color: #666; font-size: 0.9em; text-transform: uppercase; }}
        .stat-passed .stat-value {{ color: #10b981; }}
        .stat-failed .stat-value {{ color: #ef4444; }}
        .stat-skipped .stat-value {{ color: #f59e0b; }}
        .stat-total .stat-value {{ color: #3b82f6; }}
        .section {{
            padding: 40px;
            border-top: 1px solid #e5e7eb;
        }}
        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #1f2937;
        }}
        .test-group {{
            margin-bottom: 30px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}
        .test-group-header {{
            background: #f3f4f6;
            padding: 15px 20px;
            font-weight: 600;
            font-size: 1.1em;
            color: #374151;
        }}
        .test-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #f3f4f6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-item:last-child {{ border-bottom: none; }}
        .test-name {{ flex: 1; }}
        .test-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }}
        .status-passed {{
            background: #d1fae5;
            color: #065f46;
        }}
        .status-failed {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .status-skipped {{
            background: #fef3c7;
            color: #92400e;
        }}
        .test-duration {{
            color: #6b7280;
            font-size: 0.9em;
            margin-left: 10px;
        }}
        .test-details {{
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .test-error {{
            color: #dc2626;
            font-size: 0.85em;
            margin-top: 5px;
            padding: 8px;
            background: #fee2e2;
            border-radius: 4px;
        }}
        .progress-bar {{
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Crypto Monitor Test Report</h1>
            <div class="meta">
                <div>Environment: <strong>{self.config.environment.upper()}</strong></div>
                <div>Base URL: <strong>{self.config.base_url}</strong></div>
                <div>Test Date: <strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong></div>
                <div>WebSocket: <strong>{'Enabled' if self.config.websocket_enabled else 'Disabled'}</strong></div>
            </div>
        </div>
        
        <div class="summary">
            <div class="stat-card stat-total">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{summary['total']}</div>
            </div>
            <div class="stat-card stat-passed">
                <div class="stat-label">Passed</div>
                <div class="stat-value">{summary['passed']}</div>
            </div>
            <div class="stat-card stat-failed">
                <div class="stat-label">Failed</div>
                <div class="stat-value">{summary['failed']}</div>
            </div>
            <div class="stat-card stat-skipped">
                <div class="stat-label">Skipped</div>
                <div class="stat-value">{summary['skipped']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Pass Rate: {summary['pass_rate']:.1f}%</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {summary['pass_rate']}%"></div>
            </div>
            <p style="color: #6b7280; margin-top: 10px;">
                Total Duration: {summary['total_duration']:.2f}s
            </p>
        </div>
"""
        
        # API Tests Section
        if api_results:
            html += """
        <div class="section">
            <h2>📡 API Endpoint Tests</h2>
            <div class="test-group">
                <div class="test-group-header">API Endpoints</div>
"""
            for result in api_results:
                status_class = f"status-{result.status}"
                html += f"""
                <div class="test-item">
                    <div>
                        <div class="test-name">{result.test_name}</div>
                        <div class="test-details">{result.details}</div>
                        {f'<div class="test-error">{result.error}</div>' if result.error else ''}
                    </div>
                    <div style="display: flex; align-items: center;">
                        <span class="test-duration">{result.duration:.2f}s</span>
                        <span class="test-status {status_class}">{result.status.upper()}</span>
                    </div>
                </div>
"""
            html += """
            </div>
        </div>
"""
        
        # WebSocket Tests Section
        if ws_results:
            html += """
        <div class="section">
            <h2>🔌 WebSocket Tests</h2>
            <div class="test-group">
                <div class="test-group-header">WebSocket Connections</div>
"""
            for result in ws_results:
                status_class = f"status-{result.status}"
                html += f"""
                <div class="test-item">
                    <div>
                        <div class="test-name">{result.test_name}</div>
                        <div class="test-details">{result.details}</div>
                        {f'<div class="test-error">{result.error}</div>' if result.error else ''}
                    </div>
                    <div style="display: flex; align-items: center;">
                        <span class="test-duration">{result.duration:.2f}s</span>
                        <span class="test-status {status_class}">{result.status.upper()}</span>
                    </div>
                </div>
"""
            html += """
            </div>
        </div>
"""
        
        # Page Tests Section
        if page_results:
            html += """
        <div class="section">
            <h2>📄 Page Tests</h2>
"""
            for page, results in page_results.items():
                html += f"""
            <div class="test-group">
                <div class="test-group-header">{page}</div>
"""
                for result in results:
                    status_class = f"status-{result.status}"
                    html += f"""
                <div class="test-item">
                    <div>
                        <div class="test-name">{result.test_name}</div>
                        <div class="test-details">{result.details}</div>
                        {f'<div class="test-error">{result.error}</div>' if result.error else ''}
                    </div>
                    <div style="display: flex; align-items: center;">
                        <span class="test-duration">{result.duration:.2f}s</span>
                        <span class="test-status {status_class}">{result.status.upper()}</span>
                    </div>
                </div>
"""
                html += """
            </div>
"""
            html += """
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        output_path = self.reports_dir / f"report_{self.timestamp}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"🌐 HTML Report: {output_path}")
        return output_path

