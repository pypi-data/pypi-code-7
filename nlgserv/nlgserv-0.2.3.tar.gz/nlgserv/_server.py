# First we add simple nlg to the path
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "simplenlg.jar"))

# Bottle will handle the HTTP side of things
from bottle import route, run, request, response

# SimpleNLG will do the NLG generation
from simplenlg.framework import NLGFactory, CoordinatedPhraseElement, ListElement, PhraseElement
from simplenlg.lexicon import Lexicon
from simplenlg.realiser.english import Realiser
from simplenlg.features import Feature, Tense, NumberAgreement
from simplenlg.phrasespec import NPPhraseSpec

from java.lang import Boolean

# We only need one instance of these, so we'll create them globally.
lexicon = Lexicon.getDefaultLexicon()
nlgFactory = NLGFactory(lexicon)
realiser = Realiser(lexicon)

# Process the request to http://host:port/generateSentence
@route('/generateSentence', method="POST")
def process_generate_sentence_request():
    try:
        # Generate the sentence from the JSON payload.
        return realiser.realiseSentence(generate_sentence(request.json))
    except Exception, e:
        response.status = 400
        # If any exceptions are thrown, set status to 400, and return the error string
        return str(e)

def generate_sentence(json_request):
    sentence = nlgFactory.createClause() # All sentences have at least one clause.

    if "sentence" not in json_request:
        raise Exception("Request must contain a 'sentence' object.")

    s_spec = json_request["sentence"]
    
    if "subject" in s_spec:
        sentence.setSubject(expand_element(s_spec["subject"]))

    if "object" in s_spec:
        sentence.setObject(expand_element(s_spec["object"]))

    if "indirect_object" in s_spec:
        sentence.setIndirectObject(expand_element(s_spec["indirect_object"]))

    if "verb" in s_spec:
        sentence.setVerb(expand_element(s_spec["verb"]))

    if "complements" in s_spec:
        process_complements(sentence, s_spec["complements"])

    if "modifiers" in s_spec:
        process_modifiers(sentence, s_spec["modifiers"])

    if "features" in s_spec:
        process_features(sentence, s_spec["features"])

    return sentence # We need to realise as a sentence to get punctuation

def expand_element(elem):
    if type(elem)==unicode:
        # If the element is a unicode string, then it is as expanded as possible.
        return elem
    else:
        if "type" not in elem:
            raise Exception("Elements must have a type.")
        elif elem["type"] == "clause":
            # This needs to be tidied up, as it's very hacky.
            return generate_sentence({"sentence":elem["spec"]})
        elif elem["type"] == "noun_phrase":
            element = nlgFactory.createNounPhrase()
            element.setNoun(elem["head"])
            if "determiner" in elem:
                element.setDeterminer(elem["determiner"])
            if "features" in elem:
                process_features(element, elem["features"])
            if "modifiers" in elem:
                process_modifiers(element, elem["modifiers"])
            if "complements" in elem:
                process_complements(element, elem["complements"])
            return element
        elif elem["type"] == "verb_phrase":
            element = nlgFactory.createVerbPhrase()
            element.setVerb(elem["head"])
            if "features" in elem:
                process_features(element, elem["features"])
            if "modifiers" in elem:
                process_modifiers(element, elem["modifiers"])
            return element
        elif elem["type"] == "preposition_phrase":
            prepPhrase = nlgFactory.createPrepositionPhrase()
            if "noun" not in elem:
                raise Exception("Preposition phrases must have a noun.")
            nounPhrase = expand_element(elem["noun"])
            if "preposition" not in elem:
                raise Exception("Preposition phrases must have a preposition.")
            prepPhrase.addComplement(nounPhrase)
            prepPhrase.setPreposition(elem["preposition"])
            return prepPhrase
        elif elem["type"] == "coordinated_phrase":
            coordPhrase = nlgFactory.createCoordinatedPhrase()
            if "coordinates" not in elem:
                raise Exception("Coordinated phrases must have coordinates.")
            for coord in elem["coordinates"]:
                coordPhrase.addCoordinate(expand_element(coord))
            if "conjunction" in elem:
                coordPhrase.setFeature(Feature.CONJUNCTION, elem["conjunction"])
            return coordPhrase
        else:
            raise Exception("The type is unrecognised: %s" % (elem["type"],))

def process_complements(parent, comps):
    for comp in comps:
        parent.addComplement(expand_element(comp))

def process_modifiers(parent, mods):
    for mod in mods:
        parent.addModifier(expand_element(mod))

def process_features(element, f_spec):
    for feature, value in f_spec.items():
        if feature=="tense":
            if value=="past":
                element.setFeature(Feature.TENSE, Tense.PAST)
            elif value=="present":
                element.setFeature(Feature.TENSE, Tense.PRESENT)
            elif value=="future":
                element.setFeature(Feature.TENSE, Tense.FUTURE)
            else:
                raise Exception("Unrecognised tense: %s" % (value,))
        elif feature=="number":
            if value=="singular":
                element.setFeature(Feature.NUMBER, NumberAgreement.SINGULAR)
            elif value=="plural":
                element.setFeature(Feature.NUMBER, NumberAgreement.PLURAL)
            else:
                raise Exception("Unrecognised number: %s" % (value,))
        elif feature=="passive":
            if value=="true":
                element.setFeature(Feature.PASSIVE, Boolean(True))
            elif value=="false":
                element.setFeature(Feature.PASSIVE, Boolean(False))
            else:
                raise Exception("Feature.PASSIVE must either be 'true' or 'false'.")
        elif feature=="perfect":
            if value=="true":
                element.setFeature(Feature.PERFECT, Boolean(True))
            elif value=="false":
                element.setFeature(Feature.PERFECT, Boolean(False))
            else:
                raise Exception("Feature.PERFECT must either be 'true' or 'false'.")
        elif feature=="cue_phrase":
            element.setFeature(Feature.CUE_PHRASE, value)
        elif feature=="complementiser":
            element.setFeature(Feature.COMPLEMENTISER, value)
        else:
            raise Exception("Unrecognised feature: %s" % (feature,))

if __name__=="__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    print "Starting to run on %s, port %s" % (host, port)
    run(host=host, port=port)
