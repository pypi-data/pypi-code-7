from django_eulasees import models, serializers

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

class RawEulaList(generics.ListCreateAPIView):
    """ Create or get RawEula objects
    
    Without a pk, returns all RawEula objects.

    With a pk, returns just that RawEula
    """
    queryset = models.RawEula.objects.all()
    serializer_class = serializers.RawEulaSerializer


class EulaSnippetList(generics.ListCreateAPIView):
    """ Create or get EulaSnippets.

    EulaSnippets are just snippets: pieces of EULA text.
    """
    queryset = models.EulaSnippet.objects.all()
    serializer_class = serializers.EulaSnippetSerializer

class TagList(generics.ListCreateAPIView):
    """ Get all Tags, or a specific Tag if pk is supplied"""
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

class TagEulaList(generics.ListCreateAPIView):
    """ Get all TagEula's or a specific TagEula if a pk is supplied

    TagEula's are used when a Tag needs to indicate that the snippet
    being tag refers to another EULA (for example a separate privacy policy.
    """
    queryset = models.TagEula.objects.all()
    serializer_class = serializers.TagEulaSerializer

class TagIconList(generics.ListCreateAPIView):
    """ Get all TagIcon's or a specific TagEula if a pk is supplied

    TagIcons are used to associated an Icon with a specific Tag.
    """
    queryset = models.TagIcon.objects.all()
    serializer_class = serializers.TagIconSerializer

class SnippetTagList(generics.ListCreateAPIView):
    """ Get all SnippetTag's or a specific TagEula if a pk is supplied

    SnippetTags just specify which tags are associated with which snippets.
    """
    queryset = models.SnippetTag.objects.all()
    serializer_class = serializers.SnippetTagSerializer


class SnippetsForEula(generics.ListAPIView):
    """ Get all snippets for a given Eula """
    serializer_class = serializers.EulaSnippetSerializer

    def get_queryset(self):

        pk = self.kwargs.get('pk')

        # get the eula
        eula = models.RawEula.objects.get(pk=pk)

        # Return the eula snippets
        return eula.eulasnippet_set.all()

class TagsForSnippet(generics.ListAPIView):
    """ Get all tags for a given Snippet """
    serializer_class = serializers.TagSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        # get the snippet
        snippet = models.EulaSnippet.objects.get(pk=pk)

        # get the tags for all tags associated with this snippet
        return [st.tag for st in snippet.snippettag_set.all()]
    
    

class TagsForEula(generics.ListAPIView):
    """ Get all tags for a given Eula """
    serializer_class = serializers.TagSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        # get the EULA
        eula = models.RawEula.objects.get(pk=pk)

        tags = set()
        results = []

        # loop round snippets for the EULA
        for snippet in eula.eulasnippet_set.all():
            # loop round snippettag's for the snippet
            for tag in snippet.snippettag_set.all():
                if tag.tag.pk not in tags:
                    tags.add(tag.tag.pk)
                    results.append(tag.tag)
            
        return results

class EulasForTag(generics.ListAPIView):
    """ Get all Eulas for a given Tag """
    serializer_class = serializers.RawEulaSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        tag = models.Tag.objects.get(pk=pk)

        eulas = set()
        results = []
        for snippet_tag in tag.snippettag_set.all():
            eid = snippet_tag.snippet.eula.pk
            if eid not in eulas:
                eulas.add(eid)
                results.append(snippet_tag.snippet.eula)
        
        return results
    

class SnippetTagsForEula(generics.ListAPIView):
    """ Get the (snippet, tag) pairs for a EULA """
    serializer_class = serializers.SnippetTagSerializer

    def get_queryset(self):

        pk = int(self.kwargs.get('pk'))

        # get the eula
        eula = models.RawEula.objects.get(pk=pk)

        results = []
        for snippet in eula.eulasnippet_set.all():
            results += [x for x in snippet.snippettag_set.all()]

        return results


@api_view(['GET'])    
def get_everything_for_eula(request, pk):
    """ Get everything for the specified pk """

    # start with the Eula
    eula = models.RawEula.objects.get(pk=pk)
    result = serializers.RawEulaSerializer(eula).data

    # Get the snippets
    snippets = [_get_everything_for_snippet(snippet) for snippet in eula.eulasnippet_set.all()]

    result['snippets'] = snippets

    return Response(result)


def _get_everything_for_snippet(snippet):
    """ Get everything for a snippet """

    # Get tags for the snippet
    tags = [_get_everything_for_tag(x.tag) for x in snippet.snippettag_set.all()]
    
    result = serializers.EulaSnippetSerializer(snippet).data

    result['tags'] = tags

    return result

def _get_everything_for_tag(tag):

    # Get TagIcons
    icons = [serializers.TagIconSerializer(x).data for x in tag.tagicon_set.all()]
    tag_eulas = [serializers.TagEualSerializer(x).data for x in tag.tageula_set.all()]

    result = serializers.TagSerializer(tag).data
    result['icons'] = icons
    result['tag_eulas'] = tag_eulas
    
    return result
