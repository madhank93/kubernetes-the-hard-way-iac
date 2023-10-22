import pulumi
import pulumi_aws as aws
from pulumi_aws import ec2, lb, get_availability_zones
import pulumi_command as command
import os

file_path = os.path.expanduser("~/.ssh/")
public_key = open(f"{file_path}/id_rsa.pub").read()
private_key = pulumi.Output.secret(open(f"{file_path}/id_rsa").read())

vpc = ec2.Vpc(
    "vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "kubernetes-the-hard-way"},
)

availability_zone = get_availability_zones().names[0]

subnet = ec2.Subnet(
    "subnet",
    availability_zone=availability_zone,
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    tags={"Name": "kubernetes"},
)

internet_gateway = ec2.InternetGateway(
    "internet-gateway", vpc_id=vpc.id, tags={"Name": "kubernetes"}
)

route_table = ec2.RouteTable("route-table", vpc_id=vpc.id)

route_table_association = ec2.RouteTableAssociation(
    "route-table-association", route_table_id=route_table.id, subnet_id=subnet.id
)

route = ec2.Route(
    "route",
    route_table_id=route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id,
)

security_group = ec2.SecurityGroup(
    "kubernetes",
    vpc_id=vpc.id,
    description="Kubernetes security group",
    tags={"Name": "kubernetes"},
    egress=[
        {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    ingress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["10.0.0.0/16", "10.200.0.0/16"],
        },
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 443,
            "to_port": 443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "icmp",
            "from_port": 8,
            "to_port": -1,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
)

load_balancer = lb.LoadBalancer(
    "loadBalancer",
    internal=False,
    name="kubernetes",
    subnets=[subnet.id],
    load_balancer_type="network",
)

target_group = lb.TargetGroup(
    "targetGroup",
    name="kubernetes",
    protocol="TCP",
    port=6443,
    target_type="ip",
    vpc_id=vpc.id,
)


for i in range(3):
    lb.TargetGroupAttachment(
        f"target{i}", target_group_arn=target_group.arn, target_id=f"10.0.1.1{i}"
    )

listener = lb.Listener(
    "listener",
    load_balancer_arn=load_balancer.arn,
    protocol="TCP",
    port=443,
    default_actions=[{"type": "forward", "target_group_arn": target_group.arn}],
)

instance_image = pulumi.Output.from_input(
    ec2.get_ami(
        most_recent=True,
        owners=["099720109477"],
        filters=[
            {
                "name": "name",
                "values": ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"],
            },
            {
                "name": "root-device-type",
                "values": ["ebs"],
            },
            {
                "name": "architecture",
                "values": ["x86_64"],
            },
        ],
    )
)

key_pair = aws.ec2.KeyPair("ec2-key-pair", public_key=public_key)

instance_type = "t3.micro"


def create_instance(name: str):
    res = name.split(sep="-")
    name = f"{res[0]}-{res[1]}"
    private_ip = (
        f"10.0.1.2{res[1]}" if res[0].lower() == "worker" else f"10.0.1.1{res[1]}"
    )
    user_data = (
        f"name=worker-{res[1]}|pod-cidr=10.200.{res[1]}.0/24"
        if res[0].lower() == "worker"
        else name
    )
    return ec2.Instance(
        name,
        ami=instance_image.id,
        instance_type=instance_type,
        key_name=key_pair.key_name,
        vpc_security_group_ids=[security_group.id],
        subnet_id=subnet.id,
        associate_public_ip_address=True,
        user_data=user_data,
        private_ip=private_ip,
        tags={"Name": name},
        availability_zone=availability_zone,
        ebs_block_devices=[
            {
                "device_name": "/dev/sda1",
                "volume_size": 20,
                "delete_on_termination": True,
            }
        ],
    )


worker_0 = create_instance("worker-0")
worker_1 = create_instance("worker-1")
worker_2 = create_instance("worker-2")
controller_0 = create_instance("controller-0")
controller_1 = create_instance("controller-1")
controller_2 = create_instance("controller-2")


sub_cloud_env = command.local.Command(
    "substitute-cloud-env",
    create="cat ansible_vars.yml | envsubst > ansible/group_vars/all.yml && cat ansible_hosts | envsubst > ansible/hosts",
    environment={
        "CONTROL_PLANE_IP_0": controller_0.public_ip,
        "CONTROL_PLANE_IP_1": controller_1.public_ip,
        "CONTROL_PLANE_IP_2": controller_2.public_ip,
        "WORKER_PLANE_IP_0": worker_0.public_ip,
        "WORKER_PLANE_IP_1": worker_1.public_ip,
        "WORKER_PLANE_IP_2": worker_2.public_ip,
        "KUBERNETES_PUBLIC_ADDRESS": load_balancer.dns_name,
    },
)

ansible_play_run = command.local.Command(
    "run-ansible-play-book",
    create="cd ansible && ansible-playbook main.yml -i hosts --user ubuntu --key-file=~/.ssh/id_rsa",
    opts=pulumi.ResourceOptions(
        depends_on=sub_cloud_env,
    ),
)

pulumi.export("Kubernetes-Public-Address", load_balancer.dns_name)
