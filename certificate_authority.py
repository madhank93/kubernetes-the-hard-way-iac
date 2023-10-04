import subprocess
import json
from pulumi_aws import ec2
import pulumi
import pulumi_command as command
import util
import compute_resources

# Certificate authority
ca = subprocess.run(
    ["cfssl gencert -initca resource/ca-csr.json | cfssljson -bare ca"], shell=True
)

# Admin client certificate
admin_client_cert = subprocess.run(
    [
        "cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=resource/ca-config.json \
            -profile=kubernetes \
            resource/admin-csr.json | cfssljson -bare admin"
    ],
    shell=True,
)

# Controller manager client certificates

cm_cert = subprocess.run(
    [
        "cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=resource/ca-config.json \
            -profile=kubernetes \
            resource/kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager"
    ],
    shell=True,
)

# Kube proxy client certificates

kube_proxy = subprocess.run(
    [
        "cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=resource/ca-config.json \
            -profile=kubernetes \
            resource/kube-proxy-csr.json | cfssljson -bare kube-proxy"
    ],
    shell=True,
)

# Scheduler client certificates

scheduler_cert = subprocess.run(
    [
        "cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=resource/ca-config.json \
            -profile=kubernetes \
            resource/kube-scheduler-csr.json | cfssljson -bare kube-scheduler"
    ],
    shell=True,
)

# Kubernetes API server certificate

kubernetes_hostnames = (
    "kubernetes",
    "kubernetes.default",
    "kubernetes.default.svc",
    "kubernetes.default.svc.cluster",
    "kubernetes.svc.cluster.local",
)

kube_api_server = subprocess.run(
    [
        f"cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=resource/ca-config.json \
            -hostname=10.32.0.1,10.0.1.10,10.0.1.11,10.0.1.12,{compute_resources.load_balancer.dns_name},127.0.0.1,{kubernetes_hostnames} \
            -profile=kubernetes \
            resource/kubernetes-csr.json | cfssljson -bare kubernetes"
    ],
    shell=True,
)


private_key = util.get_key("kubernetes-key-pair.pem")

# Service account key pair

sa = subprocess.run(
    [
        f"cfssl gencert \
            -ca=ca.pem \
            -ca-key=ca-key.pem \
            -config=resource/ca-config.json \
            -profile=kubernetes \
            resource/service-account-csr.json | cfssljson -bare service-account"
    ],
    shell=True,
)

# Kubelet client certificates


def worker_json(instance: ec2.Instance):
    index = instance._name.split(sep="-")[1]
    instance_name = instance._name
    instance_hostname = f"ip-10-0-1-2{index}"

    csr_data = {
        "CN": f"system:node:{instance_hostname}",
        "key": {"algo": "rsa", "size": 2048},
        "names": [
            {
                "C": "US",
                "L": "Portland",
                "O": "system:nodes",
                "OU": "Kubernetes The Hard Way",
                "ST": "Oregon",
            }
        ],
    }

    with open(f"{instance_name}-csr.json", "w") as csr_file:
        json.dump(csr_data, csr_file, indent=2)

    subprocess.run(
        [
            f"cfssl gencert \
                -ca=ca.pem -ca-key=ca-key.pem\
                -config=ca-config.json \
                -hostname={instance_hostname},{instance.public_ip},{instance.private_ip} \
                -profile=kubernetes \
                {instance}-csr.json"
        ],
        shell=True,
    )


for instance in compute_resources.worker_instances:
    worker_json(instance)

# Copy the appropriate certificates and private keys to each worker instance


def copy_cert_to_worker(instance: ec2.Instance):
    index = instance._name.split(sep="-")[1]
    conn = command.remote.ConnectionArgs(
        host=instance.public_ip, private_key=private_key, user="ubuntu"
    )

    command.remote.CopyFile(
        f"copy-file ca.pem to {instance._name}",
        connection=conn,
        local_path="ca.pem",
        remote_path="ca.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file worker key pem to {instance._name}",
        connection=conn,
        local_path=f"worker-{index}-key.pem",
        remote_path=f"worker-{index}-key.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file worker pem to {instance._name}",
        connection=conn,
        local_path=f"worker-{index}.pem",
        remote_path=f"worker-{index}.pem",
    )


for instance in compute_resources.worker_instances:
    copy_cert_to_worker(instance)

# Copy the appropriate certificates and private keys to each controller instance:


def copy_cert_to_controller(instance: ec2.Instance):
    index = instance._name.split(sep="-")[1]
    # instance_name = f"controller-{index}"

    conn = command.remote.ConnectionArgs(
        host=instance.public_ip, private_key=private_key, user="ubuntu"
    )

    command.remote.CopyFile(
        f"copy-file ca.pem to {instance._name}",
        connection=conn,
        local_path="ca.pem",
        remote_path="ca.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file ca-key.pem to {instance._name}",
        connection=conn,
        local_path=f"ca-key.pem",
        remote_path=f"ca-key.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file kubernetes-key.pem to {instance._name}",
        connection=conn,
        local_path=f"kubernetes-key.pem",
        remote_path=f"kubernetes-key.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file kubernetes.pem to {instance._name}",
        connection=conn,
        local_path=f"kubernetes.pem",
        remote_path=f"kubernetes.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file service-account-key.pem to {instance._name}",
        connection=conn,
        local_path=f"service-account-key.pem",
        remote_path=f"service-account-key.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.CopyFile(
        f"copy-file service-account.pem to {instance._name}",
        connection=conn,
        local_path=f"service-account.pem",
        remote_path=f"service-account.pem",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )


for instance in compute_resources.controller_instances:
    copy_cert_to_controller(instance)

result = "Certificate authority part completed"
