from invoke import task, run


@task
def build_environment(ctx):
    print("Building environment...")
    ctx.run("docker-compose up -d")


@task(pre=[build_environment])
def process_file(ctx):
    print("Processing file...")
    ctx.run("python src/main.py process_file")

@task
def export_to_csv(ctx):
    pass
    # file_handler.export_data_to_csv()


@task(pre=[process_file])
def run(ctx):
    print("Processing ip list...")
    ctx.run("python src/main.py run")


@task
def destroy(ctx):
    print("Destroying environment....")
    ctx.run("docker-compose down")
