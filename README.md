# Kubernetes Inventory Service Lab

## Overview

This project demonstrates core Kubernetes concepts including **Deployments, Services, service discovery, readiness probes, load balancing, Pod failure, and automatic Pod replacement**.

The application consists of:

- An **Inventory Service** running with two replicas.
- A Kubernetes **Service** that exposes the Inventory Pods.
- A **client Pod** that communicates with the Inventory application using the Kubernetes Service name instead of individual Pod IP addresses.
- A **readiness probe** that controls whether an Inventory Pod is eligible to receive traffic.
- Kubernetes self-healing behavior that automatically creates a replacement when an Inventory Pod is deleted.

---

## Architecture

```text
                     Kubernetes Cluster
+-------------------------------------------------------+
|                                                       |
|                     Client Pod                        |
|                         |                             |
|                         | HTTP Request                |
|                         | http://inventory-service    |
|                         v                             |
|               +-------------------+                   |
|               | Inventory Service |                  |
|               |    ClusterIP      |                  |
|               +---------+---------+                   |
|                         |                             |
|                  Load Balancing                       |
|                    /         \                        |
|                   v           v                       |
|          +-------------+ +-------------+              |
|          | Inventory   | | Inventory   |              |
|          |   Pod 1     | |   Pod 2     |              |
|          |   Ready     | |   Ready     |              |
|          +-------------+ +-------------+              |
|                                                       |
|              Inventory Deployment                     |
|                   replicas: 2                         |
+-------------------------------------------------------+
```

The client does not communicate directly with a specific Inventory Pod. Instead, it sends requests to `inventory-service`. Kubernetes service discovery resolves this name and routes requests to available ready Pods.

---

## Technologies Used

- Kubernetes
- Minikube
- Docker
- kubectl
- Python
- Flask

---

## Project Structure

```text
kubernetes-inventory-lab/
|
|-- app.py
|-- Dockerfile
|-- deployment.yaml
|-- service.yaml
|-- client.yaml
|-- README.md
```

---

# 1. Inventory Application

The Inventory application is a simple HTTP service. Each response includes the hostname of the Pod that processed the request.

This makes it possible to demonstrate that requests sent through the Kubernetes Service can reach different Inventory replicas.

Example response:

```text
Inventory response from inventory-xxxxxxxxxx-abcde
```

---

# 2. Docker Image

The Inventory application is packaged into a Docker container using the included `Dockerfile`.

When using Minikube, the image can be built directly into Minikube's container environment.

Example:

```bash
minikube image build -t inventory-app:v1 .
```

The image can then be verified using:

```bash
minikube image ls
```

---

# 3. Inventory Deployment

The Inventory application is deployed using a Kubernetes Deployment.

The Deployment is configured with:

```yaml
replicas: 2
```

This ensures that Kubernetes maintains two Inventory Pods.

The Deployment can be created using:

```bash
kubectl apply -f deployment.yaml
```

The Pods can be checked using:

```bash
kubectl get pods
```

Expected result:

```text
NAME                         READY   STATUS    RESTARTS   AGE
inventory-xxxxxxxxxx-xxxxx   1/1     Running   0          ...
inventory-xxxxxxxxxx-xxxxx   1/1     Running   0          ...
```

Both Inventory replicas should be in the `Running` and `Ready` state.

---

# 4. Kubernetes Service

A Kubernetes Service exposes the Inventory replicas using a stable Service name:

```text
inventory-service
```

The Service is created using:

```bash
kubectl apply -f service.yaml
```

The Service can be verified using:

```bash
kubectl get services
```

The Service provides a stable endpoint even though individual Pods can be created, deleted, or replaced.

The client therefore communicates with:

```text
http://inventory-service
```

instead of using individual Pod IP addresses.

---

# 5. Client Pod

A separate client Pod is used to communicate with the Inventory Service.

The client can be created using:

```bash
kubectl apply -f client.yaml
```

Verify that it is running:

```bash
kubectl get pods
```

The client sends requests using the Kubernetes Service name.

Example:

```bash
kubectl exec client -- wget -qO- http://inventory-service
```

This demonstrates Kubernetes service discovery because `inventory-service` is resolved inside the cluster without requiring the IP address of an Inventory Pod.

---

# 6. Multiple Inventory Replicas

Multiple requests can be sent from the client to demonstrate that the Service can route traffic to more than one Inventory replica.

Example:

```bash
kubectl exec client -- sh -c "for i in 1 2 3 4 5 6 7 8 9 10; do wget -qO- http://inventory-service; echo; done"
```

Because each Inventory response contains the Pod hostname, responses from different Pod names demonstrate that multiple replicas can receive requests.

This shows that the client communicates through the Service rather than being tied to one specific Pod.

---

# 7. Readiness Probe

The Inventory Deployment includes a Kubernetes readiness probe.

Example configuration:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

The readiness probe determines whether a Pod should receive normal Service traffic.

A Pod can still be:

```text
STATUS: Running
```

while simultaneously being:

```text
READY: 0/1
```

When this happens, Kubernetes removes the Pod from the Service's ready endpoints.

---

# 8. Readiness Failure Test

To demonstrate readiness behavior, one Inventory Pod is intentionally made to fail its readiness check.

The Pod remains running, but Kubernetes marks it as unready.

Pod status can be checked using:

```bash
kubectl get pods
```

The Service endpoints can also be inspected using:

```bash
kubectl get endpoints inventory-service
```

or:

```bash
kubectl get endpointslices
```

Requests are then sent from the client again:

```bash
kubectl exec client -- sh -c "for i in 1 2 3 4 5; do wget -qO- http://inventory-service; echo; done"
```

While one Pod is unready, normal Service traffic is sent only to the remaining ready Inventory Pod.

This demonstrates an important distinction:

**Readiness failure does not necessarily terminate a Pod. It prevents the Pod from receiving normal Service traffic.**

---

# 9. Restoring Readiness

After the readiness condition is restored, Kubernetes detects that the Pod is healthy again.

The status can be checked using:

```bash
kubectl get pods
```

Both Pods should return to:

```text
READY   STATUS
1/1     Running
```

The Service endpoints can be checked again:

```bash
kubectl get endpoints inventory-service
```

Requests can then be repeated:

```bash
kubectl exec client -- sh -c "for i in 1 2 3 4 5 6 7 8 9 10; do wget -qO- http://inventory-service; echo; done"
```

After readiness is restored, the previously unready Pod becomes eligible to receive Service traffic again.

---

# 10. Pod Failure and Recovery

Kubernetes Deployments continuously attempt to maintain the desired number of replicas.

The Inventory Deployment specifies:

```yaml
replicas: 2
```

One Inventory Pod can be manually deleted to simulate a Pod failure.

First, list the Pods:

```bash
kubectl get pods
```

Then delete one Inventory Pod:

```bash
kubectl delete pod <inventory-pod-name>
```

For example:

```bash
kubectl delete pod inventory-xxxxxxxxxx-xxxxx
```

Immediately after deletion, Kubernetes detects that the Deployment has fewer replicas than requested and creates a replacement Pod.

This can be observed using:

```bash
kubectl get pods -w
```

The replacement Pod receives a different Pod name and identity from the deleted Pod.

---

# 11. Service Stability During Pod Replacement

Although an individual Inventory Pod is deleted and replaced, the Kubernetes Service does not change.

The Service can be checked using:

```bash
kubectl get service inventory-service
```

The client continues to use:

```text
http://inventory-service
```

Requests can be tested again using:

```bash
kubectl exec client -- wget -qO- http://inventory-service
```

Therefore, the client does not need to know that an Inventory Pod was deleted or replaced.

This demonstrates why Kubernetes Services provide a stable abstraction over dynamic Pods.

---

# 12. Kubernetes Self-Healing

The Pod deletion experiment demonstrates Kubernetes self-healing.

The Deployment controller continuously compares:

```text
Desired replicas = 2
Actual replicas  = 2
```

If a Pod disappears:

```text
Desired replicas = 2
Actual replicas  = 1
```

Kubernetes automatically creates another Pod until the desired state is restored.

The replacement Pod has a new identity, while the Deployment and Service remain unchanged.

---

# 13. Useful Commands

Check cluster status:

```bash
kubectl get nodes
```

Check all Pods:

```bash
kubectl get pods
```

Show additional Pod information:

```bash
kubectl get pods -o wide
```

Check the Deployment:

```bash
kubectl get deployments
```

Check Services:

```bash
kubectl get services
```

Check Inventory Service endpoints:

```bash
kubectl get endpoints inventory-service
```

Check EndpointSlices:

```bash
kubectl get endpointslices
```

Describe the Inventory Deployment:

```bash
kubectl describe deployment inventory
```

Describe a Pod:

```bash
kubectl describe pod <pod-name>
```

View application logs:

```bash
kubectl logs <pod-name>
```

Watch Pod changes:

```bash
kubectl get pods -w
```

Send a request from the client:

```bash
kubectl exec client -- wget -qO- http://inventory-service
```

---

# 14. Lab Results

The implementation demonstrates the following Kubernetes behaviors:

### Deployment and Service Discovery

- The Inventory application runs with two replicas.
- Both Inventory Pods can run simultaneously.
- A Kubernetes Service exposes the replicas.
- The client communicates using the Service name `inventory-service`.
- The client does not require individual Pod IP addresses.
- Requests can reach more than one Inventory replica.

### Readiness

- Each Inventory Pod has a readiness probe.
- A Pod can remain running while being marked unready.
- An unready Pod is removed from normal Service traffic.
- Other ready replicas continue serving requests.
- Once readiness is restored, the Pod becomes eligible to receive traffic again.

### Failure and Recovery

- An Inventory Pod can be manually deleted.
- Kubernetes automatically creates a replacement.
- The replacement has a different Pod identity/name.
- The number of desired replicas returns to two.
- The Kubernetes Service remains unchanged.
- The client continues communicating through the same Service name.

---

# 15. Key Concepts Demonstrated

## Service Discovery

Kubernetes provides internal DNS-based service discovery. The client can access the Inventory application using:

```text
inventory-service
```

instead of tracking individual Pod IP addresses.

## Load Balancing

The Kubernetes Service distributes connections among available ready Inventory Pods.

## Readiness

Readiness probes prevent Pods that are temporarily unable to serve requests from receiving normal Service traffic.

## Self-Healing

Deployments maintain the desired number of replicas. When a managed Pod disappears, Kubernetes automatically creates a replacement.

## Stable Service Endpoint

Pods are temporary and their names and IP addresses can change. A Kubernetes Service provides a stable endpoint that remains available while backend Pods are replaced.

---

# 16. Conclusion

This lab demonstrates how Kubernetes provides reliable communication and automatic recovery for containerized applications.

The Inventory application runs with two replicas behind a Kubernetes Service. The client communicates through the stable Service name rather than individual Pods. Readiness probes ensure that only ready Pods receive normal traffic, while the Deployment controller automatically replaces deleted Pods.

The experiments demonstrate three important Kubernetes principles:

1. **Service discovery and stable networking** allow clients to communicate without tracking individual Pods.
2. **Readiness probes** prevent unhealthy or temporarily unavailable Pods from receiving normal traffic.
3. **Deployments provide self-healing** by automatically replacing failed or deleted Pods.

Together, these mechanisms allow applications to remain available even when individual Pods become unready or are replaced.
