
@cli.command()
@click.pass_context
def avail(ctx):
    '''List available UPS packages'''
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    pds = ups.repos.first_avail(repos)
    for pd in sorted(pds):
        click.echo(product_to_upsargs(pd))

@cli.command()
@click.option('-f','--flavor', 
              help="Limit the platform flavor")
@click.option('-q','--qualifiers', default='',
              help="Limit the build qualifiers with a colon-separated list")
@click.argument('package')
@click.argument('version')
@click.pass_context
def resolve(ctx, flavor, qualifiers, package, version):
    repos = [ups.repos.UpsRepo(pdir) for pdir in ctx.obj['PRODUCTS']]
    pd = ups.repos.first_pvqf(repos, package, version, qualifiers, flavor)
    if pd:
        click.echo(product_to_upsargs(pd))
    return


@cli.command("install-product")
@click.option('--dryrun/--no-dryrun', default=False, help="Dry run")
@click.option('-m','--mirror', default='oink',
              help="Specify a mirror name")
@click.option('-S','--suite',
              help="Specify the suite")
@click.option('-V','--suite-version',
              help="Specify the suite version")
@click.option('-Q','--suite-qualifiers',default = '',
              help="Specify the suite version")

@click.option('-f','--flavor', 
              help="Specify platform flavor")
@click.option('-q','--qualifiers', default='',
              help="Specify build qualifiers as colon-separated list")
@click.argument('package')
@click.argument('version')
@click.pass_context
def install_product(ctx, dryrun, mirror, suite, suite_version, suite_qualifiers, flavor, qualifiers, package, version):
    '''Add the product from a suite to first configured repository.

    The <package> and <version> string may be prefaced with 're:' to
    indicate that they should be interpreted as regular expressions
    (not globs).  Otherwise they will be literally matched.
    '''
    uc = ctx.obj['commands']
    flavor = flavor or uc.flavor()
    mir = ups.mirror.make(mirror)
    if not mir:
        click.echo('No such mirror: "%s"' % mirror)
        sys.exit(1)
    mes = mir.load_manifest(suite, suite_version, flavor, suite_qualifiers)
    matdat = dict()
    if flavor: matdat['flavor'] = flavor
    if qualifiers: matdat['quals'] = qualifiers
    if package: matdat['name'] = package
    if version: matdat['version'] = version
    matmes = ups.util.match(mes, **matdat)

    repodir = ctx.obj['PRODUCTS'][0]

    if dryrun:
        print 'Dry-run, not installing these %d products' % len(matmes)
        for me in matmes:
            print '\t%s -> %s' %(me.tarball, repodir)
        return

    # fixme: make temp directory configurable
    # fixme: move this block into the a module
    repo = ups.repos.UpsRepo(repodir)
    import tempfile
    tmpdir = tempfile.mkdtemp()
    for me in matmes:
        print '\t%s -> %s/%s' %(mirror, tmpdir, me.tarball)
        tfile = mir.download(me, tmpdir)
        print '\t%s -> %s' %(me.tarball, repodir)
        repo.unpack(me, tfile)
