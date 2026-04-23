import json

# Load majors from JSON
with open('models/majors.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'✅ Tổng số ngành trong models/majors.json: {len(data)}\n')
print('=' * 80)
print('DANH SÁCH ĐẦY ĐỦ 73 NGÀNH (không dấu)\n')
print('=' * 80 + '\n')

for i, item in enumerate(data, 1):
    print(f'{i:2d}. {item["nganh"]}')
