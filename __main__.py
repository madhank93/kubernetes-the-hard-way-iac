import compute_resources
import pulumi

pulumi.export("kubernetesPublicAddress", compute_resources.load_balancer.dns_name)
