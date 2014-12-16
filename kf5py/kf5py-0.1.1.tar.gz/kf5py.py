import json
import warnings

import requests


class Connection:
    """Handle connections to the KF5 API."""

    def __init__(self, baseUrl, username, password):
        self.valid = False
        if baseUrl[-1:] != '/':
            warnings.warn('Adding / to baseUrl', RuntimeWarning)
            baseUrl = baseUrl + '/'
        auth = requests.post(baseUrl + 'rest/account/userLogin',
                             data={'userName': username, 'password': password})
        if auth.status_code == 200:
            self.valid = True
            self.baseUrl = baseUrl
            self.username = username
            self.password = password
            self.cookies = auth.cookies
            self.json = json.loads(auth.text)
            self.sectionTitleById = {}
            self.sectionIdByTitle = {}
            for e in self.json:
                self.sectionTitleById[e['sectionId']] = e['sectionTitle']
                self.sectionIdByTitle[e['sectionTitle']] = e['sectionId']
            self.postsBySectionId = {}
            self.viewsBySectionId = {}
            self.postsByViewId = {}
            # self.postsByPostId = {}

    def is_valid(self):
        """ Is the connection valid? """
        return self.valid

    def get_section_ids(self):
        """ Return the user's section IDs. """
        return self.sectionTitleById.keys()
    
    def get_section_titles(self):
        """Return the user's section titles."""
        return self.sectionIdByTitle

    def get_section_id_by_title(self, sectionTitle):
        """ Return the ID of a section given its title. """
        return self.sectionIdByTitle.get(sectionTitle)

    def get_posts_by_sectionid(self, sectionId):
        """ Return the posts in a section given the section's ID.  Some memoization is used. """
        if sectionId not in self.postsBySectionId:
            posts = requests.get(
                self.baseUrl + 'rest/content/getSectionPosts/%s' % sectionId,
                cookies=self.cookies)
            self.postsBySectionId[sectionId] = json.loads(posts.text)
        return self.postsBySectionId[sectionId]

    def get_posts_by_sectiontitle(self, sectionTitle):
        """ Return the posts in a section given the section's title. """
        return self.get_section_posts_by_id(self.getSectionIdByTitle(sectionTitle))

    def get_views_by_sectionid(self, sectionId):
        """ Return the posts in a section given the section's ID.  Some memoization is used. """
        if sectionId not in self.viewsBySectionId:
            posts = requests.get(
                self.baseUrl + 'rest/content/getSectionViews/%s' % sectionId,
                cookies=self.cookies)
            self.viewsBySectionId[sectionId] = json.loads(posts.text)
        return self.viewsBySectionId[sectionId]

    def get_views_by_sectiontitle(self, sectionTitle):
        """ Return the posts in a section given the section's title. """
        return self.get_section_views_by_id(self.get_section_id_by_title(sectionTitle))

    def get_view_by_viewid(self, viewId):
        if viewId not in self.postsByViewId:
            posts = requests.get(
                self.baseUrl + 'rest/content/getView/%s' % viewId,
                cookies=self.cookies)
            self.postsByViewId[viewId] = json.loads(posts.text)
        return self.postsByViewId[viewId]

    #def get_post_by_postid(self,postId):
    #    if postId not in self.postsByPostId:
    #        post = requests.get(
    #            self.baseUrl + 'rest/content/getPost/%s' %  postId,
    #           cookies=self.cookies)
    #        self.postsByPostId[postId] = json.loads(post.text)
    #    return self.postsByPostId[postId]
