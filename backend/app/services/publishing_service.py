import csv
import json
from pathlib import Path


def export_report_to_markdown(report_id: int, report_json: str) -> str:
    payload = json.loads(report_json or '{}')
    path = Path('backend/exports') if Path('backend').exists() else Path('exports')
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f'report-{report_id}.md'

    lines = [
        f'# Report {report_id}',
        '',
        '## Summary',
    ]
    summary = payload.get('summary', {})
    if summary:
        for key, value in summary.items():
            lines.append(f'- {key}: {value}')
    else:
        lines.append('- No summary')

    file_path.write_text('\n'.join(lines), encoding='utf-8')
    return str(file_path)


def export_report_to_csv(report_id: int, report_json: str) -> str:
    payload = json.loads(report_json or '{}')
    path = Path('backend/exports') if Path('backend').exists() else Path('exports')
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f'report-{report_id}.csv'

    summary = payload.get('summary', {})
    with file_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['metric', 'value'])
        for key, value in summary.items():
            writer.writerow([key, value])

    return str(file_path)
