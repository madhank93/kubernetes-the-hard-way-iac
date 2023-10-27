import pulumi
import compute_resources
import pod_network_routes
import dns_addon
import smoke_test

pulumi.export("Kubernetes-Public-Address", compute_resources.load_balancer.dns_name)
pulumi.export("route-table", pod_network_routes.route_tables)
pulumi.export("dns-output", dns_addon.core_dns._name)
pulumi.export("nginx-url", smoke_test.nginx_url)
