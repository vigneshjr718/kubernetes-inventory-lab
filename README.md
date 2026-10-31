# Kubernetes Inventory Service Lab

## Overview

This project deploys an Inventory Service on Kubernetes with two replicas and one client Pod. The client communicates with the Inventory Service using the stable Kubernetes Service name instead of individual Pod IP addresses.

## Architecture

```text
+---------------------+
|  inventory-client   |
|  curl client Pod    |
+----------+----------+
           |
           | http://inventory-service:8080/inventory
           v
+---------------------+
|  inventory-service  |
|      ClusterIP      |
+----------+----------+
           |
     +-----+-----+
     |           |
     v           v
+---------+   +---------+
| Pod 1   |   | Pod 2   |
|Inventory|   |Inventory|
+---------+   +---------+