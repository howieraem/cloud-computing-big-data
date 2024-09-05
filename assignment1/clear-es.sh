curl -XPUT -u 'master-user:master-user-password' 'domain-endpoint/restaurants/_delete_by_query" -H 'Content-Type: application/json' -d '{"query": {"match_all": {}}}'

