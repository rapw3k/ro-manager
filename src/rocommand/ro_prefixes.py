# ro_prefixes.py

"""
Central list of prefixes commonly used with ROs
extended to support ro model updates and extensions for earth science (01/2017) by Raul Palma
"""

__authors__ = "Graham Klyne (GK@ACM.ORG), Raul Palma"
__copyright__ = "Copyright 2011-2013, University of Oxford"
__license__ = "MIT (http://opensource.org/licenses/MIT)"

prefixes = (
   [("rdf",       "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs",      "http://www.w3.org/2000/01/rdf-schema#"),
    ("owl",       "http://www.w3.org/2002/07/owl#"),
    ("xml",       "http://www.w3.org/XML/1998/namespace"),
    ("xsd",       "http://www.w3.org/2001/XMLSchema#"),
    ("rdfg",      "http://www.w3.org/2004/03/trix/rdfg-1/"),
    ("ro",        "http://purl.org/wf4ever/ro#"),
    ("roevo",     "http://purl.org/wf4ever/roevo#"),
    ("roterms",   "http://purl.org/wf4ever/roterms#"),
    ("wfprov",    "http://purl.org/wf4ever/wfprov#"),
    ("wfdesc",    "http://purl.org/wf4ever/wfdesc#"),
    ("wf4ever",   "http://purl.org/wf4ever/wf4ever#"),
    ("ore",       "http://www.openarchives.org/ore/terms/"),
    ("ao",        "http://purl.org/ao/"),
    ("dcterms",   "http://purl.org/dc/terms/"),
    ("dc",        "http://purl.org/dc/elements/1.1/"),
    ("foaf",      "http://xmlns.com/foaf/0.1/"),
    ("minim",     "http://purl.org/minim/minim#"),
    ("result",    "http://www.w3.org/2001/sw/DataAccess/tests/result-set#"),
    ("roes",      "http://w3id.org/ro/earth-science#"),
    ("oa",        "http://www.w3.org/ns/oa#"),
    ("pav",       "http://purl.org/pav/"),
    ("swrc",      "http://swrc.ontoware.org/ontology#"),
    ("cito",      "http://purl.org/spar/cito/"),
    ("dbo",       "http://dbpedia.org/ontology/"),
    ("ov",        "http://open.vocab.org/terms/"),
    ("bibo",      "http://purl.org/ontology/bibo/"),
    ("prov",      "http://www.w3.org/ns/prov#"),
    ("geo",       "http://www.opengis.net/ont/geosparql#"),
    ("sf",        "http://www.opengis.net/ont/sf#"),
    ("gml",       "http://www.opengis.net/ont/gml#"),
    ("odrs",      "http://schema.theodi.org/odrs#"),
    ("cc",        "http://creativecommons.org/ns#"),
    ("odrl",      "http://www.w3.org/ns/odrl/2/"),
    ("geo-wgs84", "http://www.w3.org/2003/01/geo/wgs84_pos#"),
    ("voag",      "http://voag.linkedmodel.org/schema/voag#"),
    ("sch",       "https://schema.org/"),
    ("sch1",      "http://schema.org/"),
    ("pav",       "http://purl.org/pav/"),
    ("rel0",       "http://w3id.org/ro/earth-science#"),
    ("rel1",       "https://w3id.org/ro/terms/earth-science#"),
    # Workaround hack until Minim prefix handling is sorted out
    ("chembox",   "http://dbpedia.org/resource/Template:Chembox:"),
    ])

extra_prefixes = ([("",          "http://example.org/")])


def make_turtle_prefixes(extra_prefixes=[]):
    return"\n".join(["@prefix %s: <%s> ." % p for p in prefixes+extra_prefixes]) + "\n\n"


def make_sparql_prefixes(extra_prefixes=[]):
    return"\n".join(["PREFIX %s: <%s>" % p for p in prefixes+extra_prefixes]) + "\n\n"


turtle_prefixstr = make_turtle_prefixes(extra_prefixes)
sparql_prefixstr = make_sparql_prefixes(extra_prefixes)

prefix_dict = dict(prefixes)

# from rocommand.ro_prefixes import prefixes, prefix_dict, make_turtle_prefixes, make_sparql_prefixes, sparql_prefixstr

