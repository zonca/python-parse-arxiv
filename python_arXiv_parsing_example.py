"""
python_arXiv_parsing_example.py

This sample script illustrates a basic arXiv api call
followed by parsing of the results using the 
feedparser python module.

Please see the documentation at 
http://export.arxiv.org/api_help/docs/user-manual.html
for more information, or email the arXiv api 
mailing list at arxiv-api@googlegroups.com.

urllib is included in the standard python library.
feedparser can be downloaded from http://feedparser.org/ .

Author: Julius B. Lucks
Contributor: Andrea Zonca (andreazonca.com)

This is free software.  Feel free to do what you want
with it, but please play nice with the arXiv API!
"""

import urllib.request, urllib.parse, urllib.error
import feedparser

# Base api query url
base_url = 'http://export.arxiv.org/api/query?';

# Search parameters
search_query = 'all:electron' # search for electron in all fields
start = 0                     # retreive the first 5 results
max_results = 5

query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                     start,
                                                     max_results)

# Opensearch metadata such as totalResults, startIndex, 
# and itemsPerPage live in the opensearch namespase.
# Some entry metadata lives in the arXiv namespace.
# This is a hack to expose both of these namespaces in
# feedparser v4.1
feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

# perform a GET request using the base_url and query
response = urllib.request.urlopen(base_url+query).read()

# change author -> contributors (because contributors is a list)
response = response.replace('author','contributor')

# parse the response using feedparser
feed = feedparser.parse(response)

# print out feed information
print('Feed title: %s' % feed.feed.title)
print('Feed last updated: %s' % feed.feed.updated)

# print opensearch metadata
print('totalResults for this query: %s' % feed.feed.opensearch_totalresults)
print('itemsPerPage for this query: %s' % feed.feed.opensearch_itemsperpage)
print('startIndex for this query: %s'   % feed.feed.opensearch_startindex)

# Run through each entry, and print out information
for entry in feed.entries:
    print('e-print metadata')
    print('arxiv-id: %s' % entry.id.split('/abs/')[-1])
    print('Published: %s' % entry.published)
    print('Title:  %s' % entry.title)
    
    print('Authors:  %s' % ','.join(author.name for author in entry.contributors))
    
    # get the links to the abs page and pdf for this e-print
    for link in entry.links:
        if link.rel == 'alternate':
            print('abs page link: %s' % link.href)
        elif link.title == 'pdf':
            print('pdf link: %s' % link.href)
    
    # The journal reference, comments and primary_category sections live under 
    # the arxiv namespace
    try:
        journal_ref = entry.arxiv_journal_ref
    except AttributeError:
        journal_ref = 'No journal ref found'
    print('Journal reference: %s' % journal_ref)
    
    try:
        comment = entry.arxiv_comment
    except AttributeError:
        comment = 'No comment found'
    print('Comments: %s' % comment)
    
    # Since the <arxiv:primary_category> element has no data, only
    # attributes, feedparser does not store anything inside
    # entry.arxiv_primary_category
    # This is a dirty hack to get the primary_category, just take the
    # first element in entry.tags.  If anyone knows a better way to do
    # this, please email the list!
    print('Primary Category: %s' % entry.tags[0]['term'])
    
    # Lets get all the categories
    all_categories = [t['term'] for t in entry.tags]
    print('All Categories: %s' % (', ').join(all_categories))
    
    # The abstract is in the <summary> element
    print('Abstract: %s' %  entry.summary)
