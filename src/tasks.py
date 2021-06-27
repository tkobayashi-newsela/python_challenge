from invoke import task, run
from files_handler import FilesHandler as filehandler
from ip_processor import IP_Processor


@task
def build_environment(ctx):
    ctx.run("docker-compose up -d")


@task(pre=[build_environment])
def run(ctx):
    filehandler.get_ips_from_file()
    ipprocessor = IP_Processor()
    ipprocessor.start_process()


@task
def destroy(ctx):
    ctx.run("docker-compose down")
