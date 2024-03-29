import pulumi
from pulumi_kubernetes import Provider
from pulumi_kubernetes.yaml import ConfigFile
import compute_resources


k8s_provider = Provider(
    "k8s-provider",
    kubeconfig="~/.kube/config",
    opts=pulumi.ResourceOptions(
        depends_on=compute_resources.ansible_play_run,
    ),
)

core_dns = ConfigFile(
    "core-dns",
    file="deployments/coredns-1.8.yaml",
    opts=pulumi.ResourceOptions(depends_on=k8s_provider, provider=k8s_provider),
)
