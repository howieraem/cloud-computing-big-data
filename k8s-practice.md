## Push a local docker image to DockerHub
```
docker tag <local_image_name> <dockerhub_user_id>/<remote_image_name>
docker push <dockerhub_user_id>/<remote_image_name>
```

## Run a docker image from DockerHub
```
docker run -p <container_port>:<docker_host_port> -d <dockerhub_user_id>/<remote_image_name>
```

## Setup local K8s
```
minikube start
minikube tunnel
```

## Run app on K8s
```
kubectl create deploy <deploy_app_name> --image=<dockerhub_user_id>/<remote_image_name>
kubectl get deploy
kubectl scale deploy <deploy_app_name> --replicas=<replica_number>
kubectl get pods
kubectl expose deploy <deploy_app_name> --type=LoadBalancer --name <exposed_app_name> --port=<exposed_port>
```

## Explore K8s

Pods are running in an isolated, private network - so we need to proxy access to them so we can debug and interact with them. To do this, we'll use the following command to run a proxy in a second terminal window. 
```
kubectl proxy
```

Get the Pod name and query that pod directly through the proxy:
```
export POD_NAME=$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')
```

To see the output of our application:
```
curl http://localhost:8001/api/v1/namespaces/default/pods/$POD_NAME/proxy/
```

View container logs:
```
kubectl logs $POD_NAME
```

List the environment variables in the container:
```
kubectl exec $POD_NAME -- env
```

Start a bash session in the Pod's container:
```
kubectl exec -ti $POD_NAME -- bash
```

## Update App
```
kubectl set image <deploy_name> <container_name>=<new_image_path>
kubectl rollout status <deploy_name>  # confirm changes
```

Undo changes:
```
kubectl rollout undo <deploy_name>
```
