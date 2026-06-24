#!/bin/bash
# Example curl commands for testing the websearch agent

# Test health endpoint
echo "Testing health endpoint..."
curl http://localhost:8001/health
echo -e "\n"

# Test non-streaming completion
echo "Testing non-streaming completion..."
curl -X POST http://localhost:8001/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is Red Hat OpenShift?"}
    ],
    "stream": false
  }'
echo -e "\n"

# Test streaming completion
echo "Testing streaming completion..."
curl -sN -X POST http://localhost:8001/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Search for information about Kubernetes"}
    ],
    "stream": true
  }' | jq -R -r -j --stream 'scan("^data:(.*)")[]+[] | fromjson.choices[0].delta.content // empty'
echo -e "\n"

# For Kubernetes deployment, replace localhost:8001 with your route URL:
# ROUTE_URL=$(oc get route llamaindex-websearch-agent -o jsonpath='{.spec.host}')
# curl https://$ROUTE_URL/health
