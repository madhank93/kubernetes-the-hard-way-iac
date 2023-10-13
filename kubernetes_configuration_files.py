import subprocess
import compute_resources


def generate_kube_config_files(name, ip_address):
    subprocess.run(
        [
            f"kubectl config set-cluster kubernetes-the-hard-way \
                --certificate-authority=ca.pem \
                --embed-certs=true \
                --server=https://{ip_address} \
                --kubeconfig={name}.kubeconfig"
        ],
        shell=True,
    )

    subprocess.run(
        [
            f"kubectl config set-credentials system:node:{name} \
                --client-certificate={name}.pem \
                --client-key={name}-key.pem \
                --embed-certs=true \
                --kubeconfig={name}.kubeconfig"
        ],
        shell=True,
    )

    subprocess.run(
        [
            f"kubectl config set-cluster kubernetes-the-hard-way \
                --certificate-authority=ca.pem \
                --embed-certs=true \
                --server=https://{ip_address} \
                --kubeconfig={name}.kubeconfig"
        ],
        shell=True,
    )

    subprocess.run(
        [f"kubectl config use-context default --kubeconfig={name}.kubeconfig"],
        shell=True,
    )


# kubelet Kubernetes Configuration File
for instance in (
    compute_resources.worker_0,
    compute_resources.worker_1,
    compute_resources.worker_2,
):
    generate_kube_config_files(
        instance._name, f"{compute_resources.load_balancer.dns_name}:443"
    )

# kube-proxy Kubernetes Configuration File
kube_proxy = generate_kube_config_files(
    "kube-proxy", f"{compute_resources.load_balancer.dns_name}:443"
)

# kube-controller-manager Kubernetes Configuration File
kube_controller_manager = generate_kube_config_files(
    "kube-controller-manager", "127.0.0.1:6443"
)

# kube-scheduler Kubernetes Configuration File
kube_scheduler = generate_kube_config_files("kube-scheduler", "127.0.0.1:6443")

# admin Kubernetes Configuration File
admin = generate_kube_config_files("admin", "127.0.0.1:6443")
