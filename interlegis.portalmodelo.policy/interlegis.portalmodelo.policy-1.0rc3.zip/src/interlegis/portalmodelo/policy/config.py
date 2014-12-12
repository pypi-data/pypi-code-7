# -*- coding:utf-8 -*-
from interlegis.intranetmodelo.policy.utils import _add_id

import os

PROJECTNAME = 'interlegis.portalmodelo.policy'
PROFILE_ID = '{0}:default'.format(PROJECTNAME)

# content created at Plone's installation
DEFAULT_CONTENT = ('front-page', 'news', 'events', 'Members')

LOREM_DESCRIPTION = u'Este é um exemplo de notícia que pode ser criado e publicado no Portal Modelo. Você pode excluí-la e criar suas próprias notícias. Divirta-se! ;-)'
LOREM_TEXT = u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no portal, e clicar na aba <em><a href="edit">Edição</a></em>, que fica logo acima do título da notícia, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta notícia está dentro da pasta <em>notícias</em> e foi criada como exemplo, logo, pode ser excluída. Dentro desta pasta você pode criar outras notícias através do menu <em>Adicionar item...</em>, e então publicá-as através do menu <em>Estado</em>. Elas irão aparecer automaticamente na página inicial do site e você poderá selecionar as notícias de destaque no carrossel da página inicial, clicando a aba <em>Compor</em> e arrastando-as para o carrossel.</p>'
HOME_TILE_TEXT = u'<h3>Nossos Parlamentares</h3><table class="invisible"><tbody><tr><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td></tr><tr><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td><td style="text-align: center;"><a href="processo-legislativo/parlamentares"><img class="image-inline" src="imagens/rui-barbosa.jpg/image_tile" alt="Foto do Parlamentar" /><br/>Rui Barbosa</a></td></tr></tbody></table>'
CREATORS = (u'Interlegis', )

IMAGE = open(
    os.path.join(
        os.path.dirname(__file__), 'browser/static', 'bandeira-brasil.jpg')).read()

# new site structure; this dictionary defines the objects that are going to be
# created on the root of the site; it also includes information about folder
# constrains and objects to be created inside them
SITE_STRUCTURE = [
    dict(
        type='collective.cover.content',
        id='front-page',
        title=u'Página Inicial',
        description=u'Objeto que compõem a página inicial do site. (atenção: este objeto não deve ser excluído)',
        template_layout='Portal Modelo',
        excludeFromNav=True,
    ),
    dict(
        type='Document',
        id='footer-page',
        title=u'Rodapé do Portal',
        description=u'Conteúdo editável do rodapé do site. (atenção: este objeto não deve ser excluído))',
        text=u'<table class="invisible"><tbody><tr><th style="text-align:left">Institucional</th><th style="text-align:left">Atividade Legislativa</th><th style="text-align:left">Serviços</th><th style="text-align:left">Atendimento</th></tr><tr><td><ul><li><a href="institucional/acesso">Acesso</a></li><li><a href="institucional/historia">História</a></li><li><a href="institucional/funcao-e-definicao">Função e Definição</a></li><li><a href="institucional/estrutura">Estrutura</a></li><li><a href="institucional/noticias">Notícias</a></li><li><a href="institucional/eventos">Eventos</a></li><li><a href="blog">Blog</a></li></ul></td><td><ul><li><a href="processo-legislativo/parlamentares">Parlamentares</a></li><li><a href="processo-legislativo/legislaturas">Legislaturas</a></li><li><a href="processo-legislativo/@@mesa-diretora">Mesa Diretora</a></li><li><a href="processo-legislativo/comissoes">Comissões</a></li><li><a href="institucional/regimento-interno">Regimento Interno</a></li><li><a href="leis/lei-organica-municipal">Lei Orgância Municipal</a></li><li><a href="leis/legislacao-municipal">Legislação Municipal</a></li></ul></td><td><ul><li><a href="transparencia">Transparência</a></li><li><a href="ouvidoria">Informações ao Cidadão</a></li><li><a href="foruns">Fóruns</a></li><li><a href="transparencia/dados-abertos">Dados Abertos</a></li><li><a href="boletins">Boletim Informativo</a></li><li><a href="perguntas-frequentes">FAQ</a></li><li><a href="rss-info">RSS</a></li></ul></td><td><p>Endereço da Casa Legislativa, nº do prédio<br />Município, UF - CEP: 12345-678<br />Fone: (12) 3456-7890 - Fax: (09) 8765-4321<br />E-mail: <a href="mailto:atendimento@dominio.leg.br">atendimento@dominio.leg.br</a></p></td></tr></tbody></table>',
        excludeFromNav=True,
    ),
    dict(
        type='Folder',
        id='institucional',
        title=u'Sobre a Câmara',
        description=u'Seção que contém as informações básicas relacionadas à Casa Legislativa, como sua história, estrutura, eventos e notícias.',
        excludeFromNav=True,
        _addable_types=['Folder', 'File', 'Link', 'Document', 'Window'],
        _children=[
            dict(
                type='Folder',
                title=u'Acesso',
                description=u'Informações gerais de como interagir com a Casa Legislativa, presencialmente ou por qualquer meio de comunicação, tais como, fotos da sede, mapa de como chegar, endereço completo, horários de atendimento, telefones de contato, endereços de e-mail relevantes, links para serviços e o que mais for importante.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'Acesso',
                        description=u'Informações gerais de como interagir com a Casa Legislativa, presencialmente ou por qualquer meio de comunicação, tais como, fotos da sede, mapa de como chegar, endereço completo, horários de atendimento, telefones de contato, endereços de e-mail relevantes, links para serviços e o que mais for importante.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no portal, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar informações gerais de como interagir com a Casa Legislativa, presencialmente ou por qualquer meio de comunicação, tais como, fotos da sede, mapa de como chegar, endereço completo, horários de atendimento, telefones de contato, endereços de e-mail relevantes, links para serviços e o que mais for importante.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'História',
                description=u'Textos sobre a história da Casa Legislativa, desde sua criação, bem como, fotos, vídeos, áudios, entre outros.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'História',
                        description=u'Textos sobre a história da Casa Legislativa, desde sua criação, bem como, fotos, vídeos, áudios, entre outras.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no portal, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar textos sobre a história da Casa Legislativa, desde sua criação, bem como, fotos, vídeos, áudios, etc, que permitam às pessoas conhecer o seu legislativo.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Função e Definição',
                description=u'Informações sobre as funções da Casa Legislativa e definições sobre como ela funciona, bem como, sobre o Processo Legislativo, plenário, número de parlamentares, entre outras.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'Função e Definição',
                        description=u'Informações sobre as funções da Casa Legislativa e definições sobre como ela funciona, bem como, sobre o Processo Legislativo, plenário, número de parlamentares, entre outras.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no portal, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar informações sobre as funções da Casa Legislativa e definições sobre como ela funciona, bem como, sobre o Processo Legislativo, plenário, número de parlamentares, etc.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Estrutura',
                description=u'Informações sobre a estrutura organizacional da Casa Legislativa, tais como, organograma, setores, chefias e responsáveis com fotos e seus respectivos contatos.',
                _children=[
                    dict(
                        type='Document',
                        id='pagina-padrao',
                        title=u'Estrutura',
                        description=u'Informações sobre a estrutura organizacional da Casa Legislativa, tais como, organograma, setores, chefias e responsáveis com fotos e seus respectivos contatos.',
                        text=u'<p>Este é um conteúdo padrão que deve ser editado pelo usuário editor do site. Para alterá-lo basta se autenticar no portal, e clicar na aba <em><a href="pagina-padrao/edit">Edição</a></em>, que fica logo acima do título da página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>.</p><p>Esta página está dentro de uma pasta e foi selecionada como sua visão padrão. Na pasta você também pode criar outros conteúdos através do menu <em>Adicionar item...</em>, e conectá-los nesta página através de links internos com o editor visual.</p><p>Nesta página você deve publicar informações sobre a estrutura organizacional da Casa Legislativa, tais como, organograma, setores, chefias e responsáveis com fotos e seus contatos, para que os cidadãos os conheçam e possam contactá-los.</p>',
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Regimento Interno',
                description=u'Regimento Interno atualizado, que rege o seu funcionamento da Casa Legislativa e do Processo Legislativo.',
            ),
            dict(
                type='Folder',
                title=u'Notícias',
                description=u'Banco de notícias desta Casa Legislativa.',
                _addable_types=['Collection', 'Folder', 'News Item'],
                _children=[
                    dict(
                        type='Collection',
                        id='agregador',
                        title=u'Notícias',
                        description=u'Banco de notícias desta Casa Legislativa.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v='News Item',
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                    dict(
                        type='News Item',
                        title=u'Primeira Notícia',
                        description=LOREM_DESCRIPTION,
                        text=LOREM_TEXT,
                    ),
                    dict(
                        type='News Item',
                        title=u'Segunda Notícia',
                        description=LOREM_DESCRIPTION,
                        text=LOREM_TEXT,
                    ),
                    dict(
                        type='News Item',
                        title=u'Terceira Notícia',
                        description=LOREM_DESCRIPTION,
                        text=LOREM_TEXT,
                    ),
                    dict(
                        type='News Item',
                        title=u'Quarta Notícia',
                        description=LOREM_DESCRIPTION,
                        text=LOREM_TEXT,
                    ),
                ],
            ),
            dict(
                type='Folder',
                title=u'Clipping',
                description=u'Coleção de notícias publicadas por terceiros, relacionadas a esta Casa Legislativa.',
                _addable_types=['Collection', 'Folder', 'News Item'],
                _children=[
                    dict(
                        type='Collection',
                        id='agregador',
                        title=u'Clipping',
                        description=u'Coleção de notícias publicadas por terceiros, relacionadas a esta Casa Legislativa.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v='News Item',
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                ],
            ),
            dict(
                type='Folder',
                id='eventos',
                title=u'Agenda de Eventos',
                description=u'Calendário de eventos ocorridos nesta Casa Legislativa ou acontecimentos relevantes que tenham participação de parlamentares, funcionários, cidadãos em destaque, entre outros.',
                _addable_types=['Collection', 'Event', 'Folder'],
            ),
            dict(
                type='Folder',
                id='fotos',
                title=u'Galeria de Fotos',
                description=u'Galeria de fotos da Casa Legislativa, sessões, parlamentares, funcionários, eventos ocorridos, cidadãos colaboradores, entre outros.',
                _addable_types=['Collection', 'Folder', 'Image', 'Link'],
                _children=[
                    dict(
                        type='Collection',
                        title=u'Todas as Fotos',
                        description=u'Lista de todas as fotos armazenadas dentro desta pasta.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v=['Image', 'Link'],
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                ],
            ),
            dict(
                type='Folder',
                id='videos',
                title=u'Galeria de Vídeos',
                description=u'Acervo de vídeos da Casa Legislativa sobre eventos ocorridos, sessões legislativas, promocionais, informativos, entre outros, em formato MP4 e/ou serviços de streaming de multimídia pela Internet.',
                _addable_types=['Collection', 'Folder', 'File', 'Link', 'sc.embedder'],
                _children=[
                    dict(
                        type='Collection',
                        id='agregador',
                        title=u'Galeria de Vídeos',
                        description=u'Acervo de vídeos da Casa Legislativa sobre eventos ocorridos, sessões legislativas, promocionais, informativos, entre outros, em formato MP4 e/ou serviços de streaming de multimídia pela Internet.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v=['File', 'Link', 'sc.embedder'],
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                    dict(
                        type='Link',
                        title=u'Adesão à Rede Legislativa de TV e Rádio',
                        description=u'Link para a página do projeto da Câmara dos Deputados que informa como as Casas Legislativas podem aderir à Rede Legislativa de TV Digital. (este link é apenas informativo, está privado e deve ser removido)',
                        remoteUrl='http://www2.camara.leg.br/comunicacao/rede-legislativa-radio-tv',
                        state='private',
                    ),
                    dict(
                        type='Link',
                        title=u'Rede Legislativa de TV Digital',
                        description=u'Link para o vídeo em formato MP4, feito pela Câmara Municipal de São Paulo, que informa sobre o projeto da Câmara dos Deputados para disponibilizar canais de TV digital para as Casas Legislativas Brasileiras. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='http://ftp.interlegis.leg.br/interlegis/video/rede-legislativa-de-tv-digital.mp4',
                    ),
                ],
            ),
            dict(
                type='Folder',
                id='audios',
                title=u'Galeria de Áudios',
                description=u'Acervo de áudios e podcasts da Casa Legislativa sobre eventos ocorridos, sessões legislativas, promocionais, informativos, entre outros, em formato MP3 e/ou algum serviço de streaming de som pela Internet.',
                _addable_types=['Collection', 'Folder', 'File', 'Link'],
                _children=[
                    dict(
                        type='Collection',
                        title=u'Todos os Áudios',
                        description=u'Lista de todos os áudios armazenados dentro desta pasta.',
                        sort_reversed=True,
                        sort_on=u'effective',
                        limit=1000,
                        query=[
                            dict(
                                i='portal_type',
                                o='plone.app.querystring.operation.selection.is',
                                v=['File', 'Link'],
                            ),
                            dict(
                                i='path',
                                o='plone.app.querystring.operation.string.relativePath',
                                v='../',
                            ),
                        ],
                    ),
                    dict(
                        type='Link',
                        title=u'Domínio .leg.br',
                        description=u'Link para o áudio em formato MP3, da campanha de uso do domínio do legislativo brasileiro na Internet. (este link é um conteúdo de exemplo e pode ser removido)',
                        excludeFromNav=True,
                        remoteUrl='http://ftp.interlegis.leg.br/interlegis/audio/dominio-legbr.mp3',
                    ),
                ],
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Processo Legislativo',
        description=u'Seção que contém as informações relacionadas à atividade legislativa, parlamentares, legislatura atual e anteriores.',
        excludeFromNav=True,
        _addable_types=['Folder', 'File', 'Link', 'Document', 'Window'],
    ),
    dict(
        type='Folder',
        title=u'Leis',
        description=u'Seção que contém as leis válidas para o município, que poderão ser buscadas e acessadas pelos visitantes.',
        excludeFromNav=True,
        _addable_types=['Folder', 'File', 'Link', 'Document', 'Window'],
        _children=[
            dict(
                type='Folder',
                title=u'Lei Orgânica Municipal',
                description=u'Conteúdo atualizado da Lei Orgânica do Município.',
            ),
            dict(
                type='Folder',
                title=u'Legislação Municipal',
                description=u'Acervo com os textos integrais das normas jurídicas do município. (se a Casa Legislativa tiver um sistema de processo legislativo esta pasta pode ser substituída por um link)',
            ),
            dict(
                type='Link',
                title=u'Legislação Estadual',
                description=u'Link para o acervo de normas jurídicas do Estado.',
                remoteUrl='http://leis.al.uf.leg.br',
            ),
            dict(
                type='Link',
                title=u'Legislação Federal',
                description=u'Link para o acervo de normas jurídicas da República.',
                remoteUrl='http://www.planalto.gov.br/legislacao',
            ),
            dict(
                type='Link',
                title=u'Pesquisar no LexML',
                description=u'Link para a pesquisa LexML na legislação das três esferas (Municipal, Estadual e Federal) dos três poderes (Legislativo, Executivo e Judiciário).',
                remoteUrl='../lexml',
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Transparência',
        description=u'Seção que contém os dados relacionados a transparência da Casa Legislativa, como as prestações de contas, publicação de editais e licitações, formulários e links para o acesso à informação e atendimento ao cidadão.',
        excludeFromNav=True,
        _addable_types=['CSVData', 'Folder', 'File', 'Link', 'Document', 'Window'],
        _children=[
            dict(
                type='Folder',
                title=u'Orçamento e Finanças',
                description=u'Prestação de contas das receitas, despesas, repasses e transferências da Casa Legislativa e relatórios do controle interno.',
            ),
            dict(
                type='Folder',
                title=u'Licitações e Contratos',
                description=u'Publicação de editais e informações sobre os processos de licitação e contratos da Casa Legislativa.',
            ),
            dict(
                type='Folder',
                title=u'Recursos Humanos',
                description=u'Folha de pagamento, viagens, horas extras e outras informações sobre servidores, contratados, aposentados e pensionistas da Casa Legislativa.',
            ),
            dict(
                type='Folder',
                title=u'Parlamentares e Gabinetes',
                description=u'Repasses, verbas indenizatórias, cotas, subsídios, viagens e demais despesas dos parlamentares e seus gabinetes.',
            ),
            dict(
                type='Document',
                title=u'Acesso à Informação',
                description=u'Instruções sobre como fazer solicitações com base na Lei de Acesso à Informação a esta Casa Legislativa.',
                text=u'<p><a href="http://www.acessoainformacao.gov.br"><img class="image-right" src="../imagens/acesso-a-informacao.png/image_mini" alt="Acesso à Informação" /></a>A Lei de Acesso à Informação (LAI) - <a href="http://www.lexml.gov.br/urn/urn:lex:br:federal:lei:2011-11-18;12527">lei nº 12.527/2011</a> - regulamenta o direito constitucional de obter informações públicas. Essa norma entrou em vigor em 16 de maio de 2012 e criou mecanismos que possibilitam a qualquer pessoa, física ou jurídica, sem necessidade de apresentar motivo, o recebimento de informações públicas dos órgãos e entidades.</p><p>Os pedidos de informações devem ser realizados nas <a href="../institucional/acesso">instalações físicas</a> desta Casa Legislativa ou através da <a href="../ouvidoria">Ouvidoria</a> deste site. Preenchendo o formulário o cidadão receberá um número de protocolo e poderá acompanhar a tramitação do seu pedido de informação.</p><p>A LAI estabelece também um conjunto mínimo de informações que devem ser publicadas nas seções de acesso à informação dos sites dos órgãos e entidades públicas. Além da publicação das informações exigidas, os órgãos podem divulgar outros dados de interesse público por iniciativa própria, ou seja, de forma proativa.</p><p>Portanto, antes de apresentar um pedido de acesso, é importante que você verifique se a informação desejada já está disponível na seção de <a href="./">Transparência</a> deste site ou se ela já foi publicada como resposta a uma outra solicitação de informações realizada anteriormente através da <a href="../ouvidoria">Ouvidoria</a> deste site, que é o e-SIC (Sistema Eletrônico de Informações ao Cidadão) desta Casa Legislativa.</p>',
            ),
            dict(
                type='Document',
                title=u'Dados Abertos',
                description=u'Informações sobre os dados disponíveis neste portal em formato aberto e legível por máquinas.',
                text=u'<p><a href="http://commons.wikimedia.org/wiki/File:Open_Data_stickers.jpg#mediaviewer/File:Open_Data_stickers.jpg"><img class="image-right" alt="Selos de Dados Abertos" width="193" height="145" src="http://upload.wikimedia.org/wikipedia/commons/c/cc/Open_Data_stickers.jpg" /></a></p><p>De acordo com o portal de <a href="http://dados.gov.br">Dados Abertos</a> do Governo Federal e segundo a <a href="http://opendefinition.org/">definição</a> da <a href="http://okfn.org">Open Knowledge Foundation</a>, dados ou conteúdos são abertos quando qualquer pessoa pode livremente usá-los, reutilizá-los e redistribuí-los, estando sujeito a, no máximo, a exigência de creditar a sua autoria e compartilhar pela mesma licença. Isso geralmente é satisfeito pela publicação dos dados em formato aberto e sob uma <a href="http://opendefinition.org/licenses/">licença aberta</a>, como a que está declarada no rodapé deste site.</p><p>Publicamos 4 conjuntos de dados abertos em formato <a href="http://json.org/json-pt.html">JSON</a>, que podem ser acessados a partir das seguintes APIs:</p><ul><li><a href="../@@portalmodelo-json">Dados da Instituição</a></li><li><a href="../@@ombudsman-json">Dados da Ouvidoria (e-SIC)</a></li><li><a href="../@@pl-json">Dados do Processo Legislativo</a></li><li><a href="../@@transparency-json">Dados de Transparência</a></li></ul><p>Disponibilizamos ainda uma API em <a href="../apidata">/apidata</a> que fornece no mesmo formato, além dos dados já citados, todos os conteúdos publicados no site.</p><p>Além disso, cada seção do site têm um link <a href="../rss-info">RSS</a> que publica seus conteúdos disponíveis em formato RSS (RDF Site Summary 1.0).</p>',
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Links Úteis',
        description=u'Seção que contém os links para portais externos.',
        excludeFromNav=True,
        _addable_types=['Folder', 'Link'],
        _children=[
            dict(
                type='Link',
                title=u'Prefeitura Municipal',
                description=u'Portal da Prefeitura Municipal. (este link deve ser editado)',
                remoteUrl='http://www.prefeitura.uf.gov.br',
            ),
            dict(
                type='Link',
                title=u'Diario Oficial do Município',
                description=u'Site do diário oficial do município. (este link deve ser editado ou removido se não existir)',
                remoteUrl='http://diario.municipio.uf.gov.br',
            ),
            dict(
                type='Link',
                title=u'Assembleia Legislativa',
                description=u'Portal da Assembleia Legislativa do Estado. (este link deve ser editado)',
                remoteUrl='http://www.al.uf.leg.br',
            ),
            dict(
                type='Link',
                title=u'Câmara dos Deputados',
                description=u'Portal da Câmara dos Deputados Federal.',
                remoteUrl='http://www.camara.leg.br',
            ),
            dict(
                type='Link',
                title=u'Senado Federal',
                description=u'Portal do Senado Federal do Brasil.',
                remoteUrl='http://www.senado.leg.br',
            ),
            dict(
                type='Link',
                title=u'Programa Interlegis',
                description=u'Portal do Programa de Integração e Modernização do Legislativo Brasileiro.',
                remoteUrl='http://www.interlegis.leg.br',
            ),
        ],
    ),
    dict(
        type='Folder',
        id='imagens',
        title=u'Banco de Imagens',
        description=u'Banco de imagens usadas e referenciadas nos conteúdos do portal.',
        excludeFromNav=True,
        _addable_types=['Folder', 'Image', 'Link'],
    ),
    dict(
        type='Folder',
        title=u'Boletins',
        description=u'Boletins informativos da Casa Legislativa. Cadastre seu e-mail para ficar sabendo das nossas novidades.',
        excludeFromNav=True,
        _addable_types=['EasyNewsletter'],
        _children=[
            dict(
                type='EasyNewsletter',
                id='acompanhe',
                title=u'Acompanhe a Câmara',
                description=u'Receba por e-mail periodicamente o que acontece de novo na nossa Casa Legislativa.',
            ),
        ],
    ),
    dict(
        type='Folder',
        title=u'Enquetes',
        description=u'Pesquisas de opinião feitas pela Casa Legislativa.',
        excludeFromNav=True,
        _addable_types=['collective.polls.poll'],
    ),
    dict(
        type='Blog',
        id='blog',
        title=u'Blog Legislativo',
        description=u'Weblog sobre assuntos técnicos dos setores da Casa Legislativa.',
        author=u'Funcionários da Casa Legislativa',
        excludeFromNav=True,
    ),
    dict(
        type='Ploneboard',
        title=u'Fóruns',
        description=u'Fóruns de debates sobre temas importantes para o município. Exerça sua cidadania! Participe!',
        _children=[
            dict(
                type='PloneboardForum',
                title=u'Corrupção',
                description=u'Debates sobre corrupção pública e privada em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Educação',
                description=u'Debates sobre o ensino público em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Habitação',
                description=u'Debates sobre moradia e habitação em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Infraestrutura',
                description=u'Debates sobre infraestrutura urbana em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Meio Ambiente',
                description=u'Debates sobre ecologia e meio ambiente em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Saneamento',
                description=u'Debates sobre saneamento básico urbana em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Saúde',
                description=u'Debates sobre saúde pública em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Segurança',
                description=u'Debates sobre segurança pública em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Transporte',
                description=u'Debates sobre mobilidade urbana em nosso município.',
            ),
            dict(
                type='PloneboardForum',
                title=u'Tributação',
                description=u'Debates sobre tributação em nosso município.',
            ),
        ],
    ),
    dict(
        type='OmbudsOffice',
        title=u'Ouvidoria',
        description=u'Sistema eletrônico de informações ao cidadão, que controla as demandas dos cidadãos à Casa Legislativa, permitindo seu acompanhamento e pesquisa.',
        claim_types=[
            dict(claim_type='Denúncia'),
            dict(claim_type='Dúvida'),
            dict(claim_type='Elogio'),
            dict(claim_type='Pedido de Acesso à Informação'),
            dict(claim_type='Solicitação'),
            dict(claim_type='Sugestão'),
            dict(claim_type='Reclamação'),
        ],
        areas=[
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Administração'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Assessoria Legislativa e Jurídica'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Comissões'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Ouvidoria'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Secretaria Legislativa'),
            dict(responsible='Nome do Responsável pela Área', email='nome@dominio.leg.br', area='Plenário'),
        ],
    ),
    dict(
        type='Document',
        title=u'Perguntas Frequentes',
        description=u'Relação de perguntas que são feitas com frequência para a Casa Legislativa e suas respostas.',
        text=u'<img class="image-right" src="imagens/faq-logo.png/image_thumb" alt="FAQ" /><h2>Perguntas</h2><ol><li><a href="#p1">Este é um conteúdo padrão?</a></li><li><a href="#p2">Como alterar este conteúdo e compor a FAQ?</a></li></ol><br/><h2>Respostas</h2><h3>Este é um conteúdo padrão?<a name="p1"></a></h3><p>Sim, este é um conteúdo padrão que foi criado automaticamente junto com o Portal Modelo. O objetivo dele é lhe orientar a formatar a seção de perguntas e respostas do seu portal.</p><h3>Como alterar este conteúdo e compor a FAQ?<a name="p2"></a></h3><p>Para alterá-lo basta se autenticar no portal, e clicar na aba <em><a href="edit">Edição</a></em>, que fica logo acima do título desta página, então, inserir o conteúdo real e clicar no botão <em>Salvar</em>. Preste atenção na formatação, cada pergunta acima tem um link para a sua respectiva âncora aqui embaixo na resposta.</p>',
    ),
    dict(
        type='Document',
        id='rss-info',
        title=u'RSS',
        description=u'Assine os canais RSS disponíveis em cada seção do site e receba automaticamente todas as suas atualizações.',
        text=u'<p><img class="image-right" src="imagens/rss-logo.png" alt="RSS" />RSS é um recurso que serve para agregar conteúdos da web, podendo ser acessados por programas ou sites agregadores, facilitando o intercâmbio de informação e sua atualização. Uma descrição mais abrangente sobre essa tecnologia está disponível na <a href="http://pt.wikipedia.org/wiki/RSS">Wikipédia</a>.</p><p>Este site possui vários canais RSS (RDF Site Summary 1.0) habilitados. Basicamente, cada seção do site tem seu canal RSS que você pode assinar para receber automaticamente suas atualizações. Quando um novo conteúdo é publicado em um desses canais, ele é automaticamente transferido para os dispositivos que estiverem usando-o. Os principais canais são:</p><ul><li><a href="RSS">Geral (todos os conteúdos do site)</a></li><li><a href="institucional/noticias/RSS">Notícias</a></li><li><a href="institucional/eventos/RSS">Agenda</a></li><li><a href="foruns/RSS">Fóruns</a></li><li><a href="ouvidoria/RSS">Ouvidoria (e-SIC)</a></li><li><a href="blog/RSS">Blog</a></li><li><a href="enquetes/RSS">Enquetes</a></li></ul><p>Além disso, a busca do site também pode ser retornada como um canal RSS. Por exemplo, se você fizer uma busca pela palavra <em>lei</em>, mesmo após usar os filtros para melhorar o resultado, é possível usar sua URL como resposta em formato RSS, apenas trocando sua base de <a href="@@search?SearchableText=lei">@@search</a> para <a href="@@search_rss?SearchableText=lei">@@search_rss</a>.</p>',
    ),
    dict(
        type='Link',
        title=u'Manual de Uso',
        description=u'Link para o arquivo PDF do Manual do Portal Modelo 3 para Gestores de Conteúdo. (este link é apenas uma referência, está privado e pode ser removido)',
        remoteUrl='http://colab.interlegis.leg.br/raw-attachment/wiki/ProjetoPortalModelo/ManualPortalModelo3.pdf',
        state='private',
    ),
]

SITE_STRUCTURE = _add_id(SITE_STRUCTURE)
