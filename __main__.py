import compute_resources

import pulumi

pulumi.export("Kubernetes-Public-Address", compute_resources.load_balancer.dns_name)
