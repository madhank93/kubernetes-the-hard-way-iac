import compute_resources
import pulumi_command as command
import pulumi
import util

private_key = util.get_key("kubernetes-key-pair.pem")

for instance in (
    compute_resources.controller_0,
    compute_resources.controller_1,
    compute_resources.controller_2,
):
    conn = command.remote.ConnectionArgs(
        host=instance.public_ip, private_key=private_key, user="ubuntu"
    )

    command.remote.CopyFile(
        f"copy-file etcd bootstrapping script to {instance._name}",
        connection=conn,
        local_path="setup/bootstrap_etcd.sh",
        remote_path="bootstrap_etcd.sh",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

    command.remote.Command(
        f"bootstrapping etcd in {instance._name}",
        connection=conn,
        create="sh bootstrap_etcd.sh",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )

result = "Bootstrapping etcd completed"
