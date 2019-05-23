import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@click.group()
def cli():
    """cli commands for shotty"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help="lists all the snapshots including old ones")
def list_snapshots(project, list_all):
    "List ec2 snapshots"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                s.id,
                v.id,
                i.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break
    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def list_volumes(project):
    "List ec2 volumes"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
            v.id,
            i.id,
            str(v.size) + "GiB",
            v.state,
            v.encrypted and "Encrypted" or "Not Encrypted")))
    return

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def list_instances(project):
    "List ec2 instances"
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            )))
    return

@instances.command('stop')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def stop_instances(project):
    "stop ec2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("could not stop {0} ...".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def start_instances(project):
    "start ec2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("could not start {0} ...".format(i.id) + str(e))
            continue
    return

@instances.command('snapshot')
@click.option('--project', default=None, help="Only instances for project(tag project:<name>)")
def create_snapshot(project):
    "creates snapshots of ec2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Stopping instance {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()
        

        for v in i.volumes.all():    
            print("Creating snapshot of {0}...".format(i.id))
            v.create_snapshot(Description = "created by shotty")

        print("Starting instance {0}...".format(i.id))

        i.stop()
        i.wait_until_running()
    print("Done!")
        
    return

if __name__ == '__main__':
    cli()

    
    
