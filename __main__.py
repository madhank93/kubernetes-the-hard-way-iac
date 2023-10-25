import pulumi
import compute_resources
import pod_network_routes
import dns_addon

pulumi.export("Kubernetes-Public-Address", compute_resources.load_balancer.dns_name)
pulumi.export("route-table", pod_network_routes.route_tables)
pulumi.export("dns-output", dns_addon.config.resources)
