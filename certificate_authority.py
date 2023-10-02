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


def worker_json():
    for i in range(3):
        instance = f"worker-{i}"
        instance_hostname = f"ip-10-0-1-2{i}"

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

        with open(f"{instance}-csr.json", "w") as csr_file:
            json.dump(csr_data, csr_file, indent=2)

        instance = ec2.get_instance(
            filters=[
                ec2.GetInstanceFilterArgs(
                    name="tag:Name",
                    values=[f"{instance}"],
                )
            ],
            opts=pulumi.ResourceOptions(
                depends_on=compute_resources.load_balancer.dns_name
            ),
        )

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

        subprocess.run(["cfssljson", "-bare", instance], shell=True)


# Copy the appropriate certificates and private keys to each worker instance


def copy_cert_to_worker():
    for i in range(3):
        instance_name = f"worker-{i}"
        instance = ec2.get_instance(
            filters=[
                ec2.GetInstanceFilterArgs(
                    name="tag:Name",
                    values=[f"{instance_name}"],
                )
            ],
            opts=pulumi.ResourceOptions(
                depends_on=compute_resources.load_balancer.dns_name
            ),
        )

        conn = command.remote.ConnectionArgs(
            host=instance.public_ip, private_key=private_key, user="ubuntu"
        )

        command.remote.CopyFile(
            "copy-file ca.pem",
            connection=conn,
            local_path="ca.pem",
            remote_path="ca.pem",
            opts=pulumi.ResourceOptions(depends_on=ca),
        )

        command.remote.CopyFile(
            "copy-file worker key pem",
            connection=conn,
            local_path=f"worker-{i}-key.pem",
            remote_path=f"worker-{i}-key.pem",
            opts=pulumi.ResourceOptions(depends_on=ca),
        )

        command.remote.CopyFile(
            "copy-file worker pem",
            connection=conn,
            local_path=f"worker-{i}.pem",
            remote_path=f"worker-{i}.pem",
        )


# Copy the appropriate certificates and private keys to each controller instance:


def copy_cert_to_controller():
    for i in range(2):
        instance_name = f"controller-{i}"
        instance = ec2.get_instance(
            filters=[
                ec2.GetInstanceFilterArgs(
                    name="tag:Name",
                    values=[f"{instance_name}"],
                )
            ],
            opts=pulumi.ResourceOptions(
                depends_on=compute_resources.load_balancer.dns_name
            ),
        )

        conn = command.remote.ConnectionArgs(
            host=instance.public_ip, private_key=private_key, user="ubuntu"
        )

        command.remote.CopyFile(
            "copy-file ca.pem",
            connection=conn,
            local_path="ca.pem",
            remote_path="ca.pem",
            opts=pulumi.ResourceOptions(depends_on=ca),
        )

        command.remote.CopyFile(
            "copy-file ca-key.pem",
            connection=conn,
            local_path=f"ca-key.pem",
            remote_path=f"ca-key.pem",
            opts=pulumi.ResourceOptions(depends_on=ca),
        )

        command.remote.CopyFile(
            "copy-file kubernetes-key.pem",
            connection=conn,
            local_path=f"kubernetes-key.pem",
            remote_path=f"kubernetes-key.pem",
            opts=pulumi.ResourceOptions(depends_on=kube_api_server),
        )

        command.remote.CopyFile(
            "copy-file kubernetes.pem",
            connection=conn,
            local_path=f"kubernetes.pem",
            remote_path=f"kubernetes.pem",
            opts=pulumi.ResourceOptions(depends_on=kube_api_server),
        )

        command.remote.CopyFile(
            "copy-file service-account-key.pem",
            connection=conn,
            local_path=f"service-account-key.pem",
            remote_path=f"service-account-key.pem",
            opts=pulumi.ResourceOptions(depends_on=sa),
        )

        command.remote.CopyFile(
            "copy-file service-account.pem",
            connection=conn,
            local_path=f"service-account.pem",
            remote_path=f"service-account.pem",
            opts=pulumi.ResourceOptions(depends_on=sa),
        )


result = "Certificate authority part completed"
