# Cloud scripts

This repo is for small cloud related scripts.

## Install

Clone the repository

```bash
git clone https://github.com/jamatute/cloud-scripts
```

Install the dependencies

```bash
pip3 install -r requirements.txt
```

And add the desired programs to your `$PATH`

## AWS


### edit_ami

With this script you'll specify an ASG name, it will fetch the AMI used and
launch an instance with that AMI so you can edit it.

To list the available ASG of your AWS account use the command:

```bash
edit_ami.py -l
```

Once you know the ASG you want to edit execute

```bash
edit_ami.py -u my_username asg_name
```

It's important to specify your username, so if you forget to terminate the
instance, your team knows whom to blame :)

