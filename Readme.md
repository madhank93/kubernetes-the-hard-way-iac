# About

This a Kubernetes The Hard Way IaC version based on the awesome work of Kelsey Hightower's [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) and Prabhat Sharma's [kubernetes-the-hard-way-aws](https://github.com/prabhatsharma/kubernetes-the-hard-way-aws).


# Kubernetes The Hard Way - IaC

This tutorial walks you through setting up Kubernetes the hard way. This guide is not for people looking for a fully automated command to bring up a Kubernetes cluster. If that's you then check out [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine), [AWS Elastic Container Service for Kubernetes](https://aws.amazon.com/eks/) or the [Getting Started Guides](https://kubernetes.io/docs/setup).

Kubernetes The Hard Way is optimized for learning, which means taking the long route to ensure you understand each task required to bootstrap a Kubernetes cluster.

> The results of this tutorial should not be viewed as production ready, and may receive limited support from the community, but don't let that stop you from learning!

## Target Audience

The target audience for this tutorial is someone planning to support a production Kubernetes cluster and wants to understand how everything fits together.

## Cluster Details

Kubernetes The Hard Way guides you through bootstrapping a highly available Kubernetes cluster with end-to-end encryption between components and RBAC authentication.

* [kubernetes](https://github.com/kubernetes/kubernetes) v1.27.4
* [containerd](https://github.com/containerd/containerd) v1.7.7
* [coredns](https://github.com/coredns/coredns) v1.8.0
* [cni](https://github.com/containernetworking/cni) v1.3.0
* [etcd](https://github.com/etcd-io/etcd) v3.4.27

## Labs

This tutorial assumes you have access to the [Amazon Web Service](https://aws.amazon.com/). If you are looking for GCP version of this guide then look at : [https://github.com/kelseyhightower/kubernetes-the-hard-way](https://github.com/kelseyhightower/kubernetes-the-hard-way).

* [Prerequisites](docs/01-prerequisites.md)
* [Provisioning Compute Resources](docs/02-compute-resources.md)
* [Installing the Client Tools](docs/03-client-tools.md)
* Provisioning the CA and Generating TLS Certificates
* Generating Kubernetes Configuration Files for Authentication
* Generating the Data Encryption Config and Key
* Bootstrapping the etcd Cluster
* Bootstrapping the Kubernetes Control Plane
* Bootstrapping the Kubernetes Worker Nodes
* Configuring kubectl for Remote Access
* Provisioning Pod Network Routes
* Deploying the DNS Cluster Add-on
* Smoke Test
* Cleaning Up