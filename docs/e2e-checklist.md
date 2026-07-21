# Manual End-to-End Test Checklist

Run through this checklist to verify the full pipeline (Flask → Kafka → Consumer → PostgreSQL).

- [ ] 1. `docker-compose up -d` → all 3 containers (zookeeper, kafka, postgres) show "Up" via `docker ps`
- [ ] 2. `python run.py` → Flask starts without errors on port 5000
- [ ] 3. `python -m app.analytics.consumer` → consumer starts, connects, waits for messages
- [ ] 4. `curl POST /upload` with a real video → returns 201 with job_id
- [ ] 5. `curl GET /status/<job_id>` → eventually shows "completed" with resolutions + thumbnail
- [ ] 6. `curl POST /analytics/track` with a valid event → returns 202
- [ ] 7. Consumer terminal shows `[SAVED] {...}` for that event within ~1 second
- [ ] 8. `docker exec -it postgres psql -U ott_user -d ott_pipeline -c "SELECT * FROM viewer_events;"` → shows the new row
- [ ] 9. Repeat steps 6-8 with an invalid event (bad event type) → returns 400, nothing saved to DB
- [ ] 10. Stop and restart docker containers → PostgreSQL data still present (volume persistence check)