# -*- coding: utf-8 -*-
from five import grok
from interlegis.portalmodelo.policy.config import CREATORS
from interlegis.portalmodelo.policy.config import DEFAULT_CONTENT
from interlegis.portalmodelo.policy.config import IMAGE
from interlegis.portalmodelo.policy.config import HOME_TILE_TEXT
from interlegis.portalmodelo.policy.config import PROJECTNAME
from interlegis.portalmodelo.policy.config import SITE_STRUCTURE
from plone import api
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFQuickInstallerTool import interfaces as qi
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from StringIO import StringIO

import logging
import os

logger = logging.getLogger(PROJECTNAME)


class HiddenProducts(grok.GlobalUtility):

    grok.implements(qi.INonInstallable)
    grok.provides(qi.INonInstallable)
    grok.name(PROJECTNAME)

    def getNonInstallableProducts(self):
        return [
            u'Products.Ploneboard'
            u'Products.windowZ'
        ]


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        return [
            u'interlegis.portalmodelo.policy.upgrades.v2000:default'
            u'Products.Ploneboard:default'
            u'Products.Ploneboard:intranet'
            u'Products.Ploneboard:ploneboard'
            u'Products.Ploneboard:uninstall'
            u'Products.Ploneboard:zbasicboard'
            u'Products.Ploneboard:zlotsofposts'
            u'Products.windowZ:default'
        ]


# XXX: we should found a way to avoid creating default content on first place
def delete_default_content(site):
    """Delete content created at Plone's installation.
    """
    logger.info(u'Apagando conteúdo padrão do Plone')
    for item in DEFAULT_CONTENT:
        if hasattr(site, item):
            api.content.delete(site[item])
            logger.debug(u'    {0} apagado'.format(item))


# XXX: we should found a way to avoid creating default portlets on first place
def delete_default_portlets(site):
    """Delete default portlets created at Plone's installation.
    """
    def get_assignment(column):
        assert column in [u'left', u'right']
        name = u'plone.{0}column'.format(column)
        manager = getUtility(IPortletManager, name=name, context=site)
        return getMultiAdapter((site, manager), IPortletAssignmentMapping)

    logger.info(u'Apagando portlets padrão do Plone')
    for column in [u'left', u'right']:
        assignment = get_assignment(column)
        for portlet in assignment.keys():
            del assignment[portlet]
            logger.debug(u'    {0} apagado'.format(portlet))


def constrain_types(folder, addable_types):
    """Constrain addable types in folder.
    """
    folder.setConstrainTypesMode(True)
    folder.setImmediatelyAddableTypes(addable_types)
    folder.setLocallyAllowedTypes(addable_types)


def create_site_structure(root, structure):
    """Create and publish new site structure as defined in config.py."""
    for item in structure:
        id = item['id']
        title = item['title']
        description = item.get('description', u'')
        if id not in root:
            if 'creators' not in item:
                item['creators'] = CREATORS
            obj = api.content.create(root, **item)
            # publish private content
            if api.content.get_state(obj) == 'private':
                if not 'state' in item:
                    api.content.transition(obj, 'publish')
            elif obj.portal_type == 'PloneboardForum':
                api.content.transition(obj, 'make_freeforall')
            # constrain types in folder?
            if '_addable_types' in item:
                constrain_types(obj, item['_addable_types'])
            # the content has more content inside? create it
            if '_children' in item:
                create_site_structure(obj, item['_children'])
            # add an image to all news items
            if obj.portal_type == 'News Item':
                obj.setImage(IMAGE)
            # XXX: workaround for https://github.com/plone/plone.api/issues/99
            obj.setTitle(title)
            obj.setDescription(description)
            obj.reindexObject()
            logger.debug(u'    {0} criado e publicado'.format(title))
        else:
            logger.debug(u'    pulando {0}; conteúdo existente'.format(title))


def setup_csvdata_permissions(portal):
    """CSVData content type is allowed **only** within its own folder
    """
    permission = 'interlegis.portalmodelo.transparency: Add CSVData'
    roles = ('Manager', 'Site Administrator', 'Owner', 'Contributor')
    folder = portal['transparencia']
    folder.manage_permission(
        permission,
        roles=roles
    )
    logger.debug(u'Permissoes ajustadas em Transparencia')

    # Remove permission on the root of the site
    portal.manage_permission(
        permission,
        roles=(),
    )


def install_legislative_process_integration(self):
    """Install interlegis.portalmodelo.pl package.

    We need to deffer the installation of this package until the structure is
    created to avoid having to move the folder to the right position.
    """
    profile = 'profile-interlegis.portalmodelo.pl:default'
    setup_tool = api.portal.get_tool('portal_setup')
    setup_tool.runAllImportStepsFromProfile(profile)


def populate_cover(site):
    """Populate site front page. The layout is composed by 3 rows:

    1. 1 carousel tile
    2. 1 collection tiles
    3. 1 parlamientarians tile

    Populate and configure those tiles.
    """
    from cover import set_tile_configuration
    from plone.uuid.interfaces import IUUID

    cover = site['front-page']
    # first row
    tiles = cover.list_tiles('collective.cover.carousel')
    obj1 = site['institucional']['noticias']['terceira-noticia']
    obj2 = site['institucional']['noticias']['primeira-noticia']
    uuid1 = IUUID(obj1)
    uuid2 = IUUID(obj2)
    data = dict(uuids=[uuid1, uuid2])
    cover.set_tile_data(tiles[0], **data)
    set_tile_configuration(cover, tiles[0], image={'scale': 'large'})
    # second row
    tiles = cover.list_tiles('collective.cover.collection')
    obj = site['institucional']['noticias']['agregador']
    assert obj.portal_type == 'Collection'
    uuid = IUUID(obj)
    data = dict(header=u'Últimas Notícias', footer=u'Mais notícias…', uuid=uuid)
    cover.set_tile_data(tiles[0], **data)
    set_tile_configuration(
        cover,
        tiles[0],
        image=dict(order=0, scale='thumb'),
        date=dict(order=1),
        title=dict(htmltag='h3')
    )
    # third row
    tiles = cover.list_tiles('collective.cover.richtext')
    data = dict(text=HOME_TILE_TEXT)
    cover.set_tile_data(tiles[0], **data)


def set_site_default_page(site):
    """Set front page as site default page."""
    site.setDefaultPage('front-page')
    logger.info(u'Visão padrão do site estabelecida')


def get_collection_default_kwargs(portal_type):
    """Return default values used to create a collection with a query
    for certain portal types specified.

    :param portal_type: portal types to be listed in the collection
    :type portal_type: a string or a list of strings
    :returns: dictionary with defaults
    """
    assert isinstance(portal_type, str) or isinstance(portal_type, list)
    defaults = dict(
        sort_reversed=True,
        sort_on=u'created',
        limit=100,
        tableContents=False,
        customViewFields=(
            u'CreationDate',
            u'Title',
            u'review_state',
            u'EffectiveDate',
        ),
        query=[
            dict(
                i='portal_type',
                o='plone.app.querystring.operation.selection.is',
                v=portal_type,
            ),
            dict(
                i='path',
                o='plone.app.querystring.operation.string.relativePath',
                v='../',
            ),
        ],
    )
    return defaults


def set_solgemafullcalendar_view(obj):
    """Set solgemafullcalendar_view as default view on object."""
    obj.setLayout('solgemafullcalendar_view')
    logger.info(u'Visão de calendario estabelecida para {0}'.format(obj.title))


def set_galleria_view(obj):
    """Set galleria_view as default view on object."""
    obj.setLayout('galleria_view')
    logger.info(u'Visão de galeria estabelecida para {0}'.format(obj.title))


def set_flowplayer_view(obj):
    """Set flowplayer as default view on object."""
    obj.setLayout('flowplayer')
    logger.info(u'Visão de flowplayer estabelecida para {0}'.format(obj.title))


def set_atct_album_view(obj):
    """Set atct_album_view as default view on object."""
    obj.setLayout('atct_album_view')
    logger.info(u'Visão de miniaturas estabelecida para {0}'.format(obj.title))


def import_images(site):
    """Import all images inside the "import" folder of the package and import
    them inside the "Banco de Imagens" folder. We are assuming the folder
    contains only valid image files so no validation is done.
    """
    image_bank = site['imagens']
    # look inside "images" folder and import all files
    path = os.path.dirname(os.path.abspath(__file__)) + '/browser/images/'
    logger.info(u'Importando imagens')
    for name in os.listdir(path):
        with open(path + name) as f:
            image = StringIO(f.read())
        img_name = name.split('.')[0]
        title = img_name.replace('-', ' ').title()
        api.content.create(
            image_bank,
            type = 'Image',
            id = name,
            title = title,
            description = u'Esta imagem é referenciada nos conteúdos do portal.',
            image = image,
            creators = CREATORS,
        )
        logger.debug(u'    {0} importada'.format(name))


def import_photos(site):
    """Import some photos inside the "static" folder of the package and import
    them inside the "Galeria de Fotos" folder.
    """
    image_bank = site['institucional']['fotos']
    image_names = ['plenario-camara.jpg', 'plenario-senado.jpg', 'congresso-nacional.jpg']
    # look inside "static" folder and import some files
    path = os.path.dirname(os.path.abspath(__file__)) + '/browser/static/'
    logger.info(u'Importando imagens')
    for name in image_names:
        with open(path + name) as f:
            image = StringIO(f.read())
        img_name = name.split('.')[0]
        title = img_name.replace('-', ' ').title()
        api.content.create(
            image_bank,
            type = 'Image',
            id = name,
            title = title,
            description = u'Foto de demonstração, esta imagem pode ser removida.',
            image = image,
            creators = CREATORS,
        )
        logger.debug(u'    {0} importada'.format(name))


def set_default_view_on_folder(folder, object_id=''):
    """Create and publish a Document (or other content type) inside a folder
    and set it as the default view of that folder.
    """
    assert folder.portal_type == 'Folder'
    id = folder.id
    title = folder.title
    object_id = object_id or id

    # kwargs = {
    #     'description': u'',
    #     'creators': (u'Programa Interlegis', ),
    # }
    # if type == 'Collection':
    #     assert portal_type is not None
    #     kwargs = get_collection_default_kwargs('News Item')
    # obj = api.content.create(folder, type=type, title=title, **kwargs)
    # api.content.transition(obj, 'publish')

    folder.setDefaultPage(object_id)
    logger.info(u'Visão padrão criada e estabelecida para {0}'.format(title))
    # return obj


def miscelaneous_house_folder(site):
    """Set various adjustments on site content on "Sobre a Câmara" folder:

    - Set default views on subfolders
    - Set solgemafullcalendar_view view on "Eventos"
    - Set galleria_view view on "Fotos"
    - Set flowplayer view on "Áudios"
    - Set atct_album_view view on "Banco de Imagens"
    """
    folder = site['institucional']
    set_default_view_on_folder(folder['acesso'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['historia'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['funcao-e-definicao'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['estrutura'], object_id='pagina-padrao')
    set_default_view_on_folder(folder['noticias'], object_id='agregador')
    set_default_view_on_folder(folder['clipping'], object_id='agregador')
    set_default_view_on_folder(folder['videos'], object_id='agregador')

    set_solgemafullcalendar_view(folder['eventos'])
    set_galleria_view(folder['fotos'])
    set_flowplayer_view(folder['audios'])
    set_atct_album_view(site['imagens'])


def import_registry_settings(site):
    """Import registry settings; we need to do this before other stuff here,
    like using a cover layout defined there.

    XXX: I don't know if there is other way to do this on ZCML or XML.
    """
    PROFILE_ID = 'profile-interlegis.portalmodelo.policy:default'
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')


def create_feedback_poll(site):
    """Create a feedback poll."""
    folder = site['enquetes']
    poll = api.content.create(
        folder,
        'collective.polls.poll',
        title=u'Gostou do novo portal?',
        description=u'O que você achou do novo portal desta Casa Legislativa?',
        creators = CREATORS,
        options=[
            dict(option_id=0, description=u'Sim'),
            dict(option_id=1, description=u'Não'),
            dict(option_id=2, description=u'Pode melhorar'),
        ]
    )
    api.content.transition(poll, 'open')
    poll.reindexObject()
    logger.debug(u'Enquete inicial criada e publicada')


def create_youtube_video_embedder(site):
    """Create an embedder object to an Youtube video."""
    from plone.namedfile.file import NamedBlobImage
    folder = site['institucional']['videos']
    embedder = api.content.create(
        folder,
        'sc.embedder',
        url = u'https://www.youtube.com/watch?v=Sll8S1_ksfU',
        title = u'Município Brasil',
        description = u'O programa Município Brasil é desenvolvido pela TV Senado e conta com a participação das Casas Legislativas Brasileiras. (este embedder é um conteúdo de exemplo e pode ser removido)',
        creators = CREATORS,
        width = 459,
        height = 344,
        embed_html = u'<iframe width="459" height="344" src="http://www.youtube.com/embed/Sll8S1_ksfU?feature=oembed" frameborder="0" allowfullscreen></iframe>',
    )
    embedder.text = u'<p>O programa mensal mostra a repercussão de assuntos locais no Congresso Nacional e como as decisões do Legislativo impactam o dia a dia dos cidadãos. Com linguagem informal, o programa apresenta notícias, projetos, debates, serviços e um pouco de história dos 5.570 municípios brasileiros.</p>'
    path = os.path.dirname(__file__)
    data = open(os.path.join(path, 'browser/static', 'capa-video.jpg')).read()
    image = NamedBlobImage(data, 'image/jpeg', u'hqdefault.jpg')
    embedder.image = image
    api.content.transition(embedder, 'publish')
    embedder.reindexObject()
    logger.debug(u'Video embedder do youtube criado e publicado')


def set_enable_anon_name_plone_board(site):
    """Set enable_anon_name to True on portal_ploneboard."""
    pb = api.portal.get_tool('portal_ploneboard')
    pb.enable_anon_name = True
    logger.debug(u'Habilitado nome de usuario para ser exibido em posts dos Foruns')


def setup_various(context):
    marker_file = '{0}.txt'.format(PROJECTNAME)
    if context.readDataFile(marker_file) is None:
        return

    portal = api.portal.get()
    import_registry_settings(portal)
    delete_default_content(portal)
    delete_default_portlets(portal)
    create_site_structure(portal, SITE_STRUCTURE)
    setup_csvdata_permissions(portal)
    install_legislative_process_integration(portal)
    set_site_default_page(portal)
    miscelaneous_house_folder(portal)
    import_images(portal)
    import_photos(portal)
    populate_cover(portal)
    create_feedback_poll(portal)
    create_youtube_video_embedder(portal)
    set_enable_anon_name_plone_board(portal)


def fix_image_links_in_static_portlet(portal):
    """Fix image links in "midias-sociais" and "acesso-informacao" portlets. To
    make this independent portal site name we need to use `resolveuid/UID` as
    source of images instead of using a fixed URL.
    """

    def get_image_uid(image):
        """Return image UID."""
        folder = portal['imagens']
        if image in folder:
            return folder[image].UID()

    manager = getUtility(IPortletManager, name='plone.rightcolumn', context=portal)
    mapping = getMultiAdapter((portal, manager), IPortletAssignmentMapping)

    assert 'midias-sociais' in mapping
    portlet = mapping['midias-sociais']
    images = [
        'ico-facebook.png', 'ico-twitter.png', 'ico-linkedin.png',
        'ico-youtube.png', 'ico-flickr.png'
    ]
    for i in images:
        uid = 'resolveuid/' + get_image_uid(i)
        portlet.text = portlet.text.replace(i, uid)
    logger.debug(u'Links substituidos no portlet de midias sociais')

    assert 'banners' in mapping
    portlet = mapping['banners']
    image = 'acesso-a-informacao.png'
    uid = 'resolveuid/' + get_image_uid(image) + '/image_mini'
    portlet.text = portlet.text.replace(image, uid)
    logger.debug(u'Link substituido no portlet de acesso a informacao')


def set_flowplayer_portlet(portal):
    """Set target and splash objects in flowplayer radio-legislativa portlet."""
    manager = getUtility(IPortletManager, name='plone.rightcolumn', context=portal)
    mapping = getMultiAdapter((portal, manager), IPortletAssignmentMapping)

    assert 'radio-legislativa' in mapping
    portlet = mapping['radio-legislativa']
    portlet.data.splash = '/imagens/audio-player.png'
    portlet.data.target = '/institucional/audios'
    logger.debug(u'Definidos os objetos em vez dos paths no portlet da radio')


def setup_portlets(context):
    """This is called after import of portlets.xml.
    """
    marker_file = '{0}.txt'.format(PROJECTNAME)
    if context.readDataFile(marker_file) is None:
        return

    portal = api.portal.get()
    fix_image_links_in_static_portlet(portal)
    set_flowplayer_portlet(portal)

