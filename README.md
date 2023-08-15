## Codeforces data scraping project with Kafka
- Step 1: Setup Kafka Cluster on laptop and Kafka UI
- Step 2: Write a Producer to put scraped data from cloneforces into topic “codeforces”
- Step 3: Write a Consumer to consume topic “codeforces” to detect activity for a set of users ⇒ notify len Discord.

How to excute project:
- docker-compose
- ./producer.py getting_started.ini
- ./consumer.py getting_started.ini