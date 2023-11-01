import pulumi
import pulumi_command as command
import compute_resources
import dns_addon
import random
import base64
from pulumi_aws import ec2
from pulumi_kubernetes import Provider
from pulumi_kubernetes.core.v1 import Secret
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs, LabelSelectorArgs
from pulumi_kubernetes.core.v1 import (
    Service,
    ContainerArgs,
    PodTemplateSpecArgs,
    PodSpecArgs,
)


kubernetes_provider = Provider(
    "kubernetes-provider",
    kubeconfig="~/.kube/config",
    opts=pulumi.ResourceOptions(
        depends_on=dns_addon.core_dns,
    ),
)

encoded_data = base64.b64encode(b"mydata").decode("utf-8")


secret = Secret(
    "k8s-secret",
    metadata={"name": "kubernetes-the-hard-way"},
    data={"mykey": encoded_data},
    opts=pulumi.ResourceOptions(
        depends_on=kubernetes_provider, provider=kubernetes_provider
    ),
)

conn = command.remote.ConnectionArgs(
    host=compute_resources.controller_0.public_ip,
    private_key=compute_resources.private_key,
    user="ubuntu",
)

etcd_hex_dump = command.remote.Command(
    "etcd-hex-dump",
    connection=conn,
    create="sudo ETCDCTL_API=3 etcdctl get \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/etcd/ca.pem \
  --cert=/etc/etcd/kubernetes.pem \
  --key=/etc/etcd/kubernetes-key.pem\
  /registry/secrets/default/kubernetes-the-hard-way | hexdump -C",
    opts=pulumi.ResourceOptions(depends_on=secret),
).stdout

pulumi.export("hex-dump-of-etcd", etcd_hex_dump)

nginx_deployment = Deployment(
    "nginx-deployment",
    spec={
        "selector": LabelSelectorArgs(
            match_labels={
                "app": "nginx",
            }
        ),
        "replicas": 1,
        "template": PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(
                labels={
                    "app": "nginx",
                }
            ),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(name="nginx", image="nginx"),
                ]
            ),
        ),
    },
    opts=pulumi.ResourceOptions(
        depends_on=kubernetes_provider, provider=kubernetes_provider
    ),
)

node_port = random.randrange(30000, 32767)

nginx_service = Service(
    "nginx-service",
    spec={
        "type": "NodePort",
        "selector": nginx_deployment.spec.template.metadata.labels,
        "ports": [
            {
                "protocol": "TCP",
                "port": 80,
                "targetPort": 80,
                "nodePort": node_port,
            }
        ],
    },
    opts=pulumi.ResourceOptions(
        depends_on=kubernetes_provider, provider=kubernetes_provider
    ),
)

ec2.SecurityGroupRule(
    "allow-node-port",
    type="ingress",
    to_port=node_port,
    from_port=node_port,
    security_group_id=compute_resources.security_group,
    cidr_blocks=["0.0.0.0/0"],
    protocol="tcp",
)

pod_name = command.local.Command(
    "get-pod-name",
    create='kubectl get pods -l app=nginx -o jsonpath="{.items[0].metadata.name}"',
    opts=pulumi.ResourceOptions(
        depends_on=nginx_deployment,
    ),
)

pulumi.export("pod-name", pod_name)

node_name = command.local.Command(
    "node-name",
    create=pulumi.Output.all(pod_name.stdout).apply(
        lambda args: f'kubectl get pod {args[0]} --output=jsonpath="{{.spec.nodeName}}"'
    ),
    opts=pulumi.ResourceOptions(depends_on=pod_name),
)

pulumi.export("node-name", node_name.stdout)

instances = {
    "ip-10-0-1-20": compute_resources.worker_0.public_ip.apply(lambda ip: ip),
    "ip-10-0-1-21": compute_resources.worker_1.public_ip.apply(lambda ip: ip),
    "ip-10-0-1-22": compute_resources.worker_2.public_ip.apply(lambda ip: ip),
}

nginx_url = pulumi.Output.all(node_name.stdout, instances).apply(
    lambda args: f"{args[1][args[0]]}:{node_port}"
)
