import subprocess
import compute_resources
import pulumi_command as command
import pulumi
import util


encryption_key = (
    subprocess.check_output("head -c 32 /dev/urandom | base64", shell=True)
    .strip()
    .decode("utf-8")
)

yaml_content = f"""\
kind: EncryptionConfig
apiVersion: v1
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: {encryption_key}
      - identity: {{}}
"""

# Writing the content to a file named encryption-config.yaml
with open("encryption-config.yaml", "w") as file:
    file.write(yaml_content)

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
        f"copy-file encryption-config.yml to {instance._name}",
        connection=conn,
        local_path="encryption-config.yaml",
        remote_path="encryption-config.yaml",
        opts=pulumi.ResourceOptions(depends_on=instance),
    )
