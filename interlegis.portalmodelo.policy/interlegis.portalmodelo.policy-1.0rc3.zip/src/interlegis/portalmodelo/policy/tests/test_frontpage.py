# -*- coding: utf-8 -*-

from interlegis.portalmodelo.policy.testing import FUNCTIONAL_TESTING
from plone.testing.z2 import Browser

import unittest


class FrontPageTestCase(unittest.TestCase):
    """Ensure site front page has all expected elements."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_main_navigation(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()

        browser.open(portal_url)
        self.assertIn('Página Inicial', browser.contents)
        self.assertIn('Blog Legislativo', browser.contents)
        self.assertIn('Fóruns', browser.contents)
        self.assertIn('Ouvidoria', browser.contents)
        self.assertIn('Perguntas Frequentes', browser.contents)
        self.assertIn('RSS', browser.contents)

    def test_navigation_portlets(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()

        browser.open(portal_url)
        # Sobre a Câmara
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-acesso', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-historia', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-funcao-e-definicao', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-estrutura', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-regimento-interno', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-noticias', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-clipping', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-eventos', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-fotos', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-videos', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-audios', browser.contents)

        # Processo legislativo
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-parlamentares', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-legislaturas', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-mesa-diretora', browser.contents)

        # Leis
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-lei-organica-municipal', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-legislacao-municipal', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-legislacao-estadual', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-legislacao-federal', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-pesquisar-no-lexml', browser.contents)

        # Transparência
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-orcamento-e-financas', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-licitacoes-e-contratos', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-recursos-humanos', browser.contents)
        self.assertIn('navTreeItem visualNoMarker navTreeFolderish section-parlamentares-e-gabinetes', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-acesso-a-informacao', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-dados-abertos', browser.contents)

        # Links úteis
        self.assertIn('navTreeItem visualNoMarker section-prefeitura-municipal', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-diario-oficial-do-municipio', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-assembleia-legislativa', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-camara-dos-deputados', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-senado-federal', browser.contents)
        self.assertIn('navTreeItem visualNoMarker section-programa-interlegis', browser.contents)

    def test_social_networks_portlet(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        self.assertIn('Mídias Sociais', browser.contents)

    def test_video_portlet(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        self.assertIn('TV Legislativa', browser.contents)

    def test_audio_portlet(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        self.assertIn('Rádio Legislativa', browser.contents)

    def test_poll_portlet(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        self.assertIn('Gostou do novo portal?', browser.contents)

    def test_newsletter_portlet(self):
        browser = Browser(self.layer['app'])
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        self.assertIn('Acompanhe a Câmara', browser.contents)

