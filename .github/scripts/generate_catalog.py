import subprocess
import re
from datetime import datetime

# Unit_* ブランチを全取得
branches_raw = subprocess.check_output(
    ['git', 'branch', '-r', '--list', 'origin/Unit_*'], text=True
).splitlines()

catalog = {}

for branch in branches_raw:
    branch_name = branch.strip().replace('origin/', '')  # e.g. "Unit_A"
    prefix = branch_name + '_v'                          # e.g. "Unit_A_v"

    # そのブランチにマージ済みのタグを全取得し、ブランチ名プレフィックスで絞り込む
    all_tags = subprocess.check_output(
        ['git', 'tag', '--merged', 'origin/' + branch_name], text=True
    ).splitlines()

    unit_tags = [t for t in all_tags if t.startswith(prefix)]

    if unit_tags:
        def sort_key(tag):
            ver = tag[len(prefix):]          # e.g. "1-0-0"
            try:
                return [int(x) for x in ver.split('-')]
            except ValueError:
                return [0]

        tags_sorted = sorted(unit_tags, key=sort_key)
        latest = tags_sorted[-1]
        catalog[branch_name] = {
            'versions': tags_sorted,
            'latest': latest
        }

# テーブル生成
updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
table_lines = [
    '## Unit Catalog',
    '',
    f'最終更新: {updated}',
    '',
    '| ユニット名 | 最新バージョン | 全バージョン |',
    '|---|---|---|',
]
for unit, info in sorted(catalog.items()):
    versions_str = ', '.join(info['versions'])
    table_lines.append(f"| {unit} | **{info['latest']}** | {versions_str} |")

new_section = (
    '<!-- CATALOG_START -->\n'
    + '\n'.join(table_lines)
    + '\n<!-- CATALOG_END -->'
)

# README.md のマーカー間を差し替え
with open('README.md', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'<!-- CATALOG_START -->.*?<!-- CATALOG_END -->',
    new_section,
    content,
    flags=re.DOTALL
)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('README.md updated.')
print(f'Units found: {list(catalog.keys())}')
