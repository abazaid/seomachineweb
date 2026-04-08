import json
from datetime import datetime
from pathlib import Path


def build_fallback_report(days: int) -> dict:
    return {
        'generated_at': datetime.utcnow().isoformat(),
        'period_days': days,
        'summary': {
            'note': 'Fallback report because external providers are not fully configured yet.'
        },
        'top_performers': [],
        'opportunities': {
            'quick_wins': [],
            'declining_content': [],
            'low_ctr': [],
            'trending_topics': [],
            'competitor_gaps': [],
        },
        'recommendations': [
            {'title': 'Configure credentials', 'action': 'Complete settings and run connection tests again'},
            {'title': 'Re-run report', 'action': 'Trigger performance review after connectors are green'},
        ],
    }


def generate_performance_report(days: int) -> dict:
    try:
        from data_sources.modules.data_aggregator import DataAggregator

        aggregator = DataAggregator()
        report = aggregator.generate_performance_report(days=days)
        if not report:
            return build_fallback_report(days)
        return report
    except Exception:
        return build_fallback_report(days)


def report_to_markdown(report_id: int, report_data: dict) -> str:
    reports_dir = Path('backend/reports') if Path('backend').exists() else Path('reports')
    reports_dir.mkdir(parents=True, exist_ok=True)

    file_path = reports_dir / f'performance-report-{report_id}.md'
    lines = [
        f"# Performance Report #{report_id}",
        '',
        f"Generated At: {report_data.get('generated_at', datetime.utcnow().isoformat())}",
        f"Period Days: {report_data.get('period_days', 'N/A')}",
        '',
        '## Summary',
    ]

    summary = report_data.get('summary', {})
    if summary:
        for key, value in summary.items():
            lines.append(f'- {key}: {value}')
    else:
        lines.append('- No summary available')

    lines.extend(['', '## Recommendations'])
    recommendations = report_data.get('recommendations', [])
    if recommendations:
        for rec in recommendations:
            title = rec.get('title', 'Recommendation')
            action = rec.get('action', '')
            lines.append(f'- {title}: {action}')
    else:
        lines.append('- No recommendations available')

    file_path.write_text('\n'.join(lines), encoding='utf-8')
    return str(file_path)


def dump_report_json(report_data: dict) -> str:
    return json.dumps(report_data, ensure_ascii=False)
