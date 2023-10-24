import compute_resources
import pulumi_aws as aws
import pulumi


for index, instance in enumerate(
    iterable=[
        compute_resources.worker_0,
        compute_resources.worker_1,
        compute_resources.worker_2,
    ]
):
    aws.ec2.Route(
        f"route-{instance._name}",
        route_table_id=compute_resources.route_table.id,
        destination_cidr_block=f"10.200.{index}.0/24",
        network_interface_id=instance.primary_network_interface_id,
        opts=pulumi.ResourceOptions(
            depends_on=compute_resources.ansible_play_run,
        ),
    )


# Get list of route tables
route_tables = aws.ec2.get_route_tables()
