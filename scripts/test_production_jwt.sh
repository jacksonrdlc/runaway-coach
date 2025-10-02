#!/bin/bash
# Test production API with JWT

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYWI5NDM2My01ZDQ3LTQxMTgtODlhNS03M2VjMzMzMWUxZDYiLCJlbWFpbCI6ImphY2tydWRlbGljQGdtYWlsLmNvbSIsInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYXVkIjoiYXV0aGVudGljYXRlZCIsImV4cCI6MTc1OTM3MjQ5NywiaWF0IjoxNzU5Mjg2MDk3LCJpc3MiOiJodHRwczovL25reHZqY2R4aXlqYm5kanZmbXF5LnN1cGFiYXNlLmNvIn0.YUNOKiNt-t8KY5iSVEEFA9MHTz9iddRL0Wq-GGvFHYM"

curl -s -X POST "https://runaway-coach-api-203308554831.us-central1.run.app/analysis/quick-insights" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"id": "1", "distance": 5000}]' | jq
