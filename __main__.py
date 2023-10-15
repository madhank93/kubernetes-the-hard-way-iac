import compute_resources
import certificate_authority
import kubernetes_configuration_files
import bootstrapping_etcd
import pulumi

pulumi.export("Kubernetes-Public-Address", compute_resources.load_balancer.dns_name)
pulumi.export("Certificate-Authority-Result", certificate_authority.result)
pulumi.export("Kubernetes-configuration-Result", kubernetes_configuration_files.result)
pulumi.export("Bootstrapping-etcd-Result", bootstrapping_etcd.result)
