#!/usr/bin/env python
r"""
-------------------------------------------------------------------------------

This script retrieves publication data from NASA ADS and writes out each
publication as \item to a latex file. Open access information can be attached as
well.  The default output file is `publication_list.txt`.

Notes:
------

Some UTF8 characters still might not work (like greek letters in paper titles)
in which case those need to be declared in the header below, for example: 

    \DeclareUnicodeCharacter{3BC}{$\mu$}
    
The `-p` option allows to include articles in press which are read from the text
file `in_press.txt` (or some file specified by `-in`). In this case the content
is split up into `\item`s and if open access information should be attached, it
is taken from `oa_info.py`. This file should just contain something like

    OA_INPRESS = ['[OA]','[OA]','']

if there are for example three paper in press and the first two should be listed
as open access.


-------------------------------------------------------------------------------
"""
import urllib2, os, sys, re, json, codecs, argparse, subprocess
#
# set default values
#
OPENACCESS = False
CITATIONS = False
OA_INPRESS = []
AUTHOR = 'Birnstiel'
AUTHOR_F = 'Tilman'
FILE = 'publication_list.txt'
INFILE = 'in_press.txt'
DEVKEY = os.environ['ADS_DEV_KEY']
IN_PRESS = False
RUN = 'txt'
LATEX = 'pdflatex -interaction=nonstopmode'.split()
DATABASE = ''
#
# handle command line arguments
#
if __name__ == '__main__':
    RTHF = argparse.RawTextHelpFormatter
    PARSER = argparse.ArgumentParser()
    PARSER = argparse.ArgumentParser(description=__doc__,formatter_class=RTHF)

    GROUP = PARSER.add_mutually_exclusive_group()
    GROUP.add_argument('-oa', '--openaccess',\
        help='include open access information', action='store_true')
    GROUP.add_argument('-c', '--citations',\
        help='include citation information', action='store_true')
    PARSER.add_argument('-r', '--run',\
        help='what output to produce:\n'+\
        r'`txt` = just `\item`s'+'\n'+\
        '`tex` = full latex document\n'+\
        '`pdf` = compiled pdf file\n'+\
        'default=' + RUN,\
        choices=['txt', 'tex', 'pdf'],\
        type=str, default=RUN)
    PARSER.add_argument('-p', '--in-press',\
        help='include articles in press', action='store_true')
    PARSER.add_argument('-db', '--database',\
        help='select database, e.g. `astronomy`',\
        type=str, default=DATABASE)
    PARSER.add_argument('-a', '--author',\
        help='Last name of Author, default='+AUTHOR,\
        type=str, default=AUTHOR)
    PARSER.add_argument('-i', '--initial',\
        help='Authors first name, default='+AUTHOR_F,\
        type=str, default=AUTHOR_F)
    PARSER.add_argument('-d', '--devkey',\
        help='NASA ADS Dev Key, default=' + DEVKEY,\
        type=str, default=DEVKEY)
    PARSER.add_argument('-out', '--output',\
        help='output file, default=' + FILE,\
        type=str, default=FILE)
    PARSER.add_argument('-in', '--input',\
        help='in-press input file, default=' + INFILE,\
        type=str, default=INFILE)
    PARSER.add_argument('-l', '--latex',\
        help='latex command, default=' + ' '.join(LATEX),\
        type=str, default=' '.join(LATEX))
    ARGS = PARSER.parse_args()

    OPENACCESS = ARGS.openaccess
    CITATIONS = ARGS.citations

    RUN = ARGS.run

    IN_PRESS = ARGS.in_press
    DATABASE = ARGS.database.lower()
    AUTHOR = ARGS.author
    AUTHOR_F = ARGS.initial
    DEVKEY = ARGS.devkey
    FILE = ARGS.output
    INFILE = ARGS.input
    LATEX = ARGS.latex.split()
#
# print promotion
#
print('-----------------------')
print('Publication List Script')
print('-----------------------\n')
print('by Til Birnstiel')
print('https://github.com/birnstiel/get_publications\n')
#
# process options
#
if DEVKEY == '':
    print('\nERROR:\n' +
          'You need to specify a valid NASA ADS\n' +
          'developer key, either by setting the\n' +
          'environment variable `ADS_DEV_KEY` or\n' +
          'by using the argument `-d`.\n')
    sys.exit(1)
#
# display some information
#
print('Script will create publication list (file `{}`) for author: {} {}\n'.\
      format(os.path.splitext(FILE)[0] + '.' + RUN, AUTHOR_F, AUTHOR))
if OPENACCESS:
    from oa_info import OA_INPRESS
    print('- Including open access information')

if CITATIONS:
    print('- Including citations')

if RUN in ['tex', 'pdf']:
    FILE = os.path.splitext(FILE)[0] + '.tex'
if RUN == 'txt':
    FILE = os.path.splitext(FILE)[0] + '.txt'
#
# set header and footer of the latex document
#
HEAD = r"""
\documentclass[11pt,letterpaper]{amsart}
\usepackage[margin=3cm]{geometry}
\usepackage{enumitem}
\usepackage[utf8]{inputenc}
\DeclareUnicodeCharacter{3B1}{$\alpha$}
\DeclareUnicodeCharacter{3B4}{$\delta$}
\DeclareUnicodeCharacter{3BC}{$\mu$}
\usepackage{etaremune}
\usepackage{xspace}
\input{abbrev.tex}
%%%%%%%%%%%%%%%%%%%%%%
\usepackage{fancyhdr}
\usepackage{lastpage}
\renewcommand{\headrulewidth}{0pt}
\fancyhf{}
\fancyfoot[C]{%
  \vspace{0.5cm}\small\emph{Page \thepage\ of \pageref{LastPage}}
}
\pagestyle{fancy}
\thispagestyle{fancy}
%%%%%%%%%%%%%%%%%%%%%%
\begin{document}

\begin{center}
\uppercase{{\large\textbf{List of Publications}}}\\
\vspace{0.3cm}
\textsc{-- FIRSTNAME LASTNAME --}\\
\end{center}
\begin{etaremune}[topsep=0pt,itemsep=0.5ex,partopsep=1ex,parsep=1ex]
"""
HEAD = HEAD.replace('FIRSTNAME', AUTHOR_F + '.' * (len(AUTHOR_F) == 1))
HEAD = HEAD.replace('LASTNAME', AUTHOR)
FOOT = r'\end{etaremune}'+'\n'+r'\end{document}'+'\n'

def replace_journal_name(journal):
    """
    Replace some of the journal names with default abbreviations
    as found in many journals, see for example here:

    http://doc.adsabs.harvard.edu/abs_doc/aas_macros.sty
    http://www.aanda.org/doc_journal/instructions/aa_instructions.pdf
    """
    if journal == u'Annual Review of Astronomy and Astrophysics':
        return r'\araa'
    elif journal == u'Astronomische Nachrichten':
        return r'AN'
    elif journal == u'Astronomy and Astrophysics':
        return r'\aap'
    elif journal == u'Geochimica et Cosmochimica Acta Supplement':
        return r'GCA'
    elif journal == u'Icarus':
        return r'Icarus'
    elif journal == u'Monthly Notices of the Royal Astronomical Society':
        return r'\mnras'
    elif journal == u'Nature':
        return r'\nat'
    elif journal == u'Ph.D. Thesis':
        return r'PhD Thesis'
    elif journal == u'Physical Review D':
        return r'\prd'
    elif journal == u'Physical Review Letters':
        return r'\prl'
    elif journal == u'Protostars and Planets V':
        return r'PPV'
    elif journal == u'Science':
        return r'\sci'
    elif journal == u'The Astronomical Journal':
        return r'\aj'
    elif journal == u'The Astrophysical Journal':
        return r'\apj'
    elif journal == u'The Astrophysical Journal Supplement Series':
        return r'\apjs'
#
# read in_press file
#
sys.stdout.write('- reading from {} ... '.format(INFILE))
sys.stdout.flush()
if IN_PRESS:
    PUBS_INPRESS = re.findall('\\\\item.*', open(INFILE).read())
print('Done ')
#
# get the publication data via the ADS API
#
sys.stdout.write('- getting publication data from NASA ADS ... ')
sys.stdout.flush()
URL = r'http://adslabs.org/adsabs/api/search/?q=author:"' + AUTHOR + ',+' +\
    AUTHOR_F[0] + '"&filter=property:refereed&rows=200&dev_key=' + DEVKEY
PUBS = json.load(urllib2.urlopen(URL))['results']['docs']
print('Done')
#
# apply the filter
#
N_PUBS = len(PUBS)
if DATABASE != '':
    PUBS = [p for p in PUBS if any([db.lower() == DATABASE.lower() \
                                    for db in p['database']])]
if len(PUBS) < N_PUBS:
    print('- FILTERED OUT {:d} PUBLICATIONS'.format(N_PUBS - len(PUBS)))
#
# open file to write out results
#
sys.stdout.write('- writing files ... ')
sys.stdout.flush()
FID = codecs.open(FILE, 'w', 'utf-8')
if RUN in ['tex', 'pdf']:
    FID.write(HEAD)
#
# write in_press articles
#
if IN_PRESS:
    for i, pub in enumerate(PUBS_INPRESS):
        if OPENACCESS:
            if OA_INPRESS[i] != '':
                pub = pub + ' ' + OA_INPRESS[i]
        FID.write((pub + '\n').decode("utf-8"))
#
# convert each publication in a latex item
#
for pub in PUBS:
    string = r'\item '
    #
    # get last names
    #
    authors = [a.split(',')[0] for a in pub['author']]
    #
    # boldface author if initial matches
    #
    idx = authors.index(AUTHOR)
    if pub['author'][idx].split(',')[1][1] == AUTHOR_F[0]:
        authors[idx] = r'\textbf{' + authors[idx] + '}'
    #
    # format with commas between, and finish with ", and lastauthor"
    #
    if len(authors) == 1:
        authors = authors[0]
    elif len(authors) == 2:
        authors = ' and '.join(authors)
    else:
        authors = ', '.join(authors[0:-1]) + ', and ' + authors[-1]
    string += authors + ': '
    #
    # fix special characters in the title
    #
    title = pub['title'][0]
    specials = ['{', '}', '_', '$', '^']
    for c in specials:
        title = title.replace(c, '\\' + c)
    title = r'\textit{' + title + '}'
    string += title + ', '
    journal = replace_journal_name(pub['pub'])
    year = pub['pubdate'][0:4]
    string += journal + ' (' + year + ')'
    if 'volume' in pub.keys():
        volume = pub['volume']
        page = pub['page'][0]
        string += ', vol. ' + volume + ', ' + page
    string += '.'
    #
    # append the open access property
    #
    if OPENACCESS:
        if 'OPENACCESS' in pub['property']:
            #
            # paper is open access
            #
            string += ' [OA]'
        elif any(['arXiv' in i for i in pub['identifier']]):
            #
            # paper is on arxiv
            #
            string += ' [OA]*'
    #
    # citation count
    #
    if CITATIONS:
        c = pub['citation_count']
        string += ' [{:d} citation{}]'.format(c, 's' * (c != 1))
    #
    # write it out
    #
    FID.write(string + '\n')
#
# append open access legend
#
if OPENACCESS:
    FID.write('\\\\[1em] \n[OA] = gold open access \\\\[0em] \n'+\
              '[OA]* = green open access')
if CITATIONS:
    FID.write('\\\\[1em] \n Total number of citations: {:d}'.\
              format(sum([pub['citation_count'] for pub in PUBS])))

if RUN in ['tex', 'pdf']:
    FID.write(FOOT)
FID.close()
print('Done')

if RUN == 'pdf':
    sys.stdout.write('- compiling latex file `{:}` ... '.format(FILE))
    sys.stdout.flush()
    #
    # run latex twice
    #
    for i in range(2):
        try:
            p = subprocess.Popen(LATEX + [FILE], stderr=subprocess.PIPE,\
                                 stdout=subprocess.PIPE)
            ret_out, ret_err = p.communicate()
            ret_val = p.poll()
        except OSError as err:
            ret_out = "OSError({0}): {1}".format(err.errno, err.strerror)
    print('Done')
    #
    # clean up
    #
    for ext in ['aux', 'log', 'tex']:
        os.unlink(os.path.splitext(FILE)[0] + '.' + ext)

print('\nScript finished!\n')
