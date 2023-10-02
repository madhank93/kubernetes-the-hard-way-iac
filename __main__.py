import compute_resources
import certificate_authority
import pulumi

pulumi.export("kubernetesPublicAddress", compute_resources.load_balancer.dns_name)
pulumi.export("kubernetesPublicAddress", certificate_authority.result)
