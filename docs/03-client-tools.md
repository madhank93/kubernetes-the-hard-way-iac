# Installing the Client Tools

In this section we will use Ansible to install the command line utilities [cfsl](https://github.com/cloudflare/cfssl) and [kubectl](https://kubernetes.io/docs/tasks/tools/) in the host machine.

## Install CFSSL

The `cfssl` and `cfssljson` command line utilities will be used to provision a [PKI Infrastructure](https://en.wikipedia.org/wiki/Public_key_infrastructure) and generate TLS certificates.

Below [ansible script](/ansible/roles/client-tools/tasks/prerequisite.yml) download and installs cfssl and cfssljson. And the version to be downloaded is specified in the [ansible_vars](/ansible_vars.yml) yaml file

```yaml
- name: Install cfssl
  ansible.builtin.get_url:
    url: https://github.com/cloudflare/cfssl/releases/download/v{{ cfssl.version }}/cfssl_{{ cfssl.version }}_{{ os.name }}_{{ os.arch }}
    dest: /usr/local/bin/cfssl
    mode: a+x

- name: Install cfssljson
  ansible.builtin.get_url:
    url: https://github.com/cloudflare/cfssl/releases/download/v{{ cfssl.version }}/cfssljson_{{ cfssl.version }}_{{ os.name }}_{{ os.arch }}
    dest: /usr/local/bin/cfssljson
    mode: a+x
```

### Verification

Verify `cfssl` and `cfssljson` is installed:

```
cfssl version
```

> output

```
Version: 1.6.4
Runtime: go1.18
```

```
cfssljson --version
```

> output

```
Version: 1.6.4
Runtime: go1.18
```

## Install kubectl

The `kubectl` command line utility is used to interact with the Kubernetes API Server. Download and install `kubectl` using the [ansible script](/ansible/roles/client-tools/tasks/prerequisite.yml). And the version of `kubectl` to be downloaded is specified in the [ansible_vars](/ansible_vars.yml) yaml file.

```yaml
- name: Install kubectl
  ansible.builtin.get_url:
    url: https://dl.k8s.io/release/v{{ kubectl.version }}/bin/{{ os.name }}/{{ os.arch }}/kubectl
    dest: /usr/local/bin/kubectl
    mode: a+x
```

### Verification

Verify `kubectl` is installed:

```
kubectl version
```

> output

```
Client Version: version.Info{Major:"1", Minor:"27", GitVersion:"v1.27.4", GitCommit:"fa3d7990104d7c1f16943a67f11b154b71f6a132", GitTreeState:"clean", BuildDate:"2023-07-19T12:20:54Z", GoVersion:"go1.20.6", Compiler:"gc", Platform:"linux/amd64"}