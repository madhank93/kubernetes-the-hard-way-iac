import subprocess
import compute_resources
import pulumi_command as command
import util
import pulumi


def generate_kube_config_files(name, ip_address, user):
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
            f"kubectl config set-credentials {user} \
                --client-certificate={name}.pem \
                --client-key={name}-key.pem \
                --embed-certs=true \
                --kubeconfig={name}.kubeconfig"
        ],
        shell=True,
    )

    subprocess.run(
        [
            f"kubectl config set-context default \
                --cluster=kubernetes-the-hard-way \
                --user={user} \
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
        instance._name,
        f"{compute_resources.load_balancer.dns_name}:443",
        f"system:node:{instance._name}",
    )

# kube-proxy Kubernetes Configuration File
kube_proxy = generate_kube_config_files(
    "kube-proxy", f"{compute_resources.load_balancer.dns_name}:443", "system:kube-proxy"
)

# kube-controller-manager Kubernetes Configuration File
kube_controller_manager = generate_kube_config_files(
    "kube-controller-manager",
    "127.0.0.1:6443",
    "system:kube-controller-manager",
)

# kube-scheduler Kubernetes Configuration File
kube_scheduler = generate_kube_config_files(
    "kube-scheduler", "127.0.0.1:6443", "system:kube-scheduler"
)

# admin Kubernetes Configuration File
admin = generate_kube_config_files("admin", "127.0.0.1:6443", "admin")


private_key = util.get_key("kubernetes-key-pair.pem")


# Copy the appropriate kubelet and kube-proxy kubeconfig files to each worker instance
for instance in (
    compute_resources.worker_0,
    compute_resources.worker_1,
    compute_resources.worker_2,
):
    conn = command.remote.ConnectionArgs(
        host=instance.public_ip, private_key=private_key, user="ubuntu"
    )

    command.remote.CopyFile(
        f"copy-file kubelet kubeconfig to {instance._name}",
        connection=conn,
        local_path=f"{instance._name}.kubeconfig",
        remote_path=f"{instance._name}.kubeconfig",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file kube-proxy kubeconfig to {instance._name}",
        connection=conn,
        local_path="kube-proxy.kubeconfig",
        remote_path="kube-proxy.kubeconfig",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

# Copy the appropriate admin, kube-controller-manager and kube-scheduler kubeconfig files to each controller instance
for instance in (
    compute_resources.controller_0,
    compute_resources.controller_1,
):
    conn = command.remote.ConnectionArgs(
        host=instance.public_ip, private_key=private_key, user="ubuntu"
    )

    command.remote.CopyFile(
        f"copy-file admin kube-config to {instance._name}",
        connection=conn,
        local_path="admin.kubeconfig",
        remote_path="admin.kubeconfig",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file kube-controller-manager kube-config to {instance._name}",
        connection=conn,
        local_path="kube-controller-manager.kubeconfig",
        remote_path="kube-controller-manager.kubeconfig",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file kube-scheduler kube-config to {instance._name}",
        connection=conn,
        local_path="kube-scheduler.kubeconfig",
        remote_path="kube-scheduler.kubeconfig",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

result = "Kubernetes configuration files part completed"
