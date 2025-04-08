# NewsAnalytics

**NewsAnalytics** — це проєкт з побудови дата-стрімінгового пайплайну для збору, обробки, зберігання та аналітики 
новинних подій у реальному часі. Метою є побудувати та продемонструвати повний цикл обробки стрімінгових даних — 
від збору новин із зовнішніх джерел до побудови аналітичного дашборду.


## 🔧 Використані технології
- GNews API / RSS Feeds
- Apache Kafka
- Apache Flink / Spark Structured Streaming (в Docker на EC2/WPS сервері)
- Apache Iceberg
- Amazon S3
- AWS Glue
- Amazon Athena
- Apache Airflow
- dbt
- Great Expectations
- Apache Superset

---

## 1. Збір новин (GNews API + RSS Feeds)
**Стан:** ✅ *Завершено*

**Опис:**  
Парсинг новин з GNews API та RSS-стрічок. 
Отримані новини зберігаються у форматі JSON у папку data/raw/.
В папку logs пишуться логи процесу

📂 **Каталог:** `src/data/rss_collector.py, data/raw/, logs/`

---

## 2. Відправлення подій у Kafka
**Стан:** ⏳ *В розробці*

**Опис:**  
Відправлення зібраних новин (у форматі JSON) у Kafka-топік news_raw. Кожна подія містить метадані, джерело, 
короткий опис, дату публікації та поля для подальшого аналізу. 
📂 **Каталог:** `streaming/kafka_producer/`

---

## 2. Стрімінгова обробка подій (Spark / Flink)
**Стан:** ⏳ *В розробці*

**Опис:**  
Обробка потоку подій у Spark (або Flink): парсинг, фільтрація, збагачення, агрегація. Запуск у Docker на EC2/WPS-сервері.

📂 **Каталог:** `streaming/spark_job/` або `streaming/flink_job/`

---

## 3. Зберігання у Iceberg + S3
**Стан:** ⏳ *В розробці*

**Опис:**  
Збереження оброблених даних у форматі Apache Iceberg з підтримкою snapshot'ів та time-travel.

📂 **Каталог:** `storage/iceberg_config/`, `data/processed/`

---

## 4. Оркестрація пайплайну (Apache Airflow)
**Стан:** ⏳ *В розробці*

**Опис:**  
Оркестрація потоків даних, оновлень, перевірок якості та запуску ETL-джобів через DAG-и.

📂 **Каталог:** `pipelines/dags/`, `pipelines/plugins/`

---

## 5. Побудова моделей у dbt
**Стан:** ⏳ *В розробці*

**Опис:**  
Побудова SQL-моделей з оброблених даних (в dbt), які агрегують інформацію про новини для подальшої візуалізації.

📂 **Каталог:** `dbt/news_analytics_dbt/`

---

## 6. Перевірка якості даних
**Стан:** ⏳ *В розробці*

**Опис:**  
Використання кастомних правил та інструментів на кшталт Great Expectations для перевірки валідності даних.

📂 **Каталог:** `src/validation/`, `src/utils/logger.py`

---

## 7. Візуалізація в Superset
**Стан:** ⏳ *В розробці*

**Опис:**  
Побудова аналітичного дашборду: активність новин, топ-джерела, категорії, хронологія.

📂 **Каталог:** `dashboard/superset_config/`

---

## 8. Тестування
**Стан:** ⏳ *В розробці*

**Опис:**  
Юніт-тести для перевірки ETL-логіки та інших компонентів пайплайну.

📂 **Каталог:** `tests/test_etl.py`

---

## 📌 To-Do
- [✅] Парсинг RSS і GNews API
- [ ] Відправлення подій у Kafka
- [ ] Обробка подій у Spark / Flink
- [ ] Збереження в Iceberg на S3
- [ ] DAG-и для Airflow
- [ ] SQL-моделі у dbt
- [ ] Валідація даних
- [ ] Дашборд у Superset
- [ ] Написання тестів

---

## 📄 Ліцензія
Apache License
