# smokerfitbot
телеграм бот для проекта Физкультура Курильщика

Для генерации упражнений из .xlsx файла

```python .\scripts\export_exercises_to_json.py --file .\smokerfitbot_list.xlsx```

Для генерации SQL скрипта из JSON

```python .\scripts\json_to_sql.py --in .\data\exercises.json --out .\data\postgre_exercises.sql```

Скрипт чистит таблицу exercises каждый раз и накатывает с нуля.