import json

majors = json.load(open('models/majors.json', encoding='utf-8'))
print(f'Total majors: {len(majors)}')
print('\nMajors:')
for m in majors:
    print(f'  - {m["nganh"]}')
