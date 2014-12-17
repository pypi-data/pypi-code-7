import json
import warnings

import requests


class Connection:
    """
    Handle connections to the KF5 API.
    """

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
            self.buildonsBySectionId = {}
            self.buildonsByViewId = {}
            self.buildonsByViewId = {}
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
        return self.get_posts_by_sectionid(self.get_section_id_by_title(sectionTitle))

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
        return self.get_views_by_sectionid(self.get_section_id_by_title(sectionTitle))

    def get_view_by_viewid(self, viewId):
        if viewId not in self.postsByViewId:
            posts = requests.get(
                self.baseUrl + 'rest/content/getView/%s' % viewId,
                cookies=self.cookies)
            self.postsByViewId[viewId] = json.loads(posts.text)
        return self.postsByViewId[viewId]

    def get_buildons_by_sectiontitle(self, sectionTitle):
        """ Return the buildons in a section given the section's title. """
        return self.get_buildons_by_sectionid(self.get_section_id_by_title(sectionTitle))   
    def get_buildons_by_sectionid(self, sectionId):
        """ 
        Return list of build-on links for an entire section, given the ID of the section.  
        For example:
            [
                {
                    "type":"buildson",
                    "from":"f07ca24b-850a-420f-bfe9-bdb865b030b5",
                    "to":"ac10b2ab-b25c-4ede-8c72-3238b7322672"
                },
                    {"type":"buildson",
                    "from":"20f72522-4d62-4d89-907c-c32b447a54dc",
                    "to":"add053d2-296a-40c9-b2e5-b53ed4b31e3d"
                }
            ]

        """
        if sectionId not in self.buildonsBySectionId:
            posts = requests.get(
                self.baseUrl + 'rest/mobile/getBuildsOnInCommunity/%s' % sectionId,
                cookies=self.cookies)
            self.buildonsBySectionId[sectionId] = json.loads(posts.text)
        return self.buildonsBySectionId[sectionId]

    def get_buildons_by_viewid(self, viewId):
        """ Return list of build-on links for an entire section, given the title of the section. """
        if viewId not in self.buildonsByViewId:
            posts = requests.get(
                self.baseUrl + 'rest/mobile/getBuildsOnInView/%s' % viewId,
                cookies=self.cookies)
            self.buildonsByViewId[viewId] = json.loads(posts.text)
        return self.buildonsByViewId[viewId]

    def get_buildons_by_postid(self, postId):
        """ 
        Return list of build-on links for an entire section, given the ID of the section.
        """
        if viewId not in self.buildonsByPostId:
            posts = requests.get(
                self.baseUrl + 'rest/mobile/getBuildsOnInPost/%s' % postId,
                cookies=self.cookies)
            self.buildonsByPostId[postId] = json.loads(posts.text)
        return self.buildonsByPostId[postId]

    def get_post_history(self, postId):
        history = requests.get(
            self.baseUrl + 'rest/mobile/getPostHistory/%s' % postId,
                cookies=self.cookies)
        return json.loads(history.text)

    def get_all_authors(self, sectionId):
        authors = requests.get(
            self.baseUrl + 'rest/mobile/getAllAuthors/%s' % sectionId,
                cookies=self.cookies)
        return json.loads(authors.text)


    #def get_post_by_postid(self,postId):
    #    if postId not in self.postsByPostId:
    #        post = requests.get(
    #            self.baseUrl + 'rest/content/getPost/%s' %  postId,
    #           cookies=self.cookies)
    #        self.postsByPostId[postId] = json.loads(post.text)
    #    return self.postsByPostId[postId]
