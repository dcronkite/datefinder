import regex as re

DIGITS_MODIFIER_PATTERN = '\d+st|\d+th|\d+rd|first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|next|last'
DIGITS_PATTERN = '\d+'
DAYS_PATTERN = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun'
MONTHS_PATTERN = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar' \
                 '|apr|may|jun|jul|aug|sep|sept|oct|nov|dec '
TIMEZONES_PATTERN = 'ACDT|ACST|ACT|ACWDT|ACWST|ADDT|ADMT|ADT|AEDT|AEST|AFT|AHDT|AHST|AKDT|AKST|AKTST|AKTT|ALMST|ALMT' \
                    '|AMST|AMT|ANAST|ANAT|ANT|APT|AQTST|AQTT|ARST|ART|ASHST|ASHT|AST|AWDT|AWST|AWT|AZOMT|AZOST|AZOT' \
                    '|AZST|AZT|BAKST|BAKT|BDST|BDT|BEAT|BEAUT|BIOT|BMT|BNT|BORT|BOST|BOT|BRST|BRT|BST|BTT|BURT|CANT' \
                    '|CAPT|CAST|CAT|CAWT|CCT|CDDT|CDT|CEDT|CEMT|CEST|CET|CGST|CGT|CHADT|CHAST|CHDT|CHOST|CHOT|CIST' \
                    '|CKHST|CKT|CLST|CLT|CMT|COST|COT|CPT|CST|CUT|CVST|CVT|CWT|CXT|ChST|DACT|DAVT|DDUT|DFT|DMT|DUSST' \
                    '|DUST|EASST|EAST|EAT|ECT|EDDT|EDT|EEDT|EEST|EET|EGST|EGT|EHDT|EMT|EPT|EST|ET|EWT|FET|FFMT|FJST' \
                    '|FJT|FKST|FKT|FMT|FNST|FNT|FORT|FRUST|FRUT|GALT|GAMT|GBGT|GEST|GET|GFT|GHST|GILT|GIT|GMT|GST|GYT' \
                    '|HAA|HAC|HADT|HAE|HAP|HAR|HAST|HAT|HAY|HDT|HKST|HKT|HLV|HMT|HNA|HNC|HNE|HNP|HNR|HNT|HNY|HOVST' \
                    '|HOVT|HST|ICT|IDDT|IDT|IHST|IMT|IOT|IRDT|IRKST|IRKT|IRST|ISST|IST|JAVT|JCST|JDT|JMT|JST|JWST' \
                    '|KART|KDT|KGST|KGT|KIZST|KIZT|KMT|KOST|KRAST|KRAT|KST|KUYST|KUYT|KWAT|LHDT|LHST|LINT|LKT|LMT|LMT' \
                    '|LMT|LMT|LRT|LST|MADMT|MADST|MADT|MAGST|MAGT|MALST|MALT|MART|MAWT|MDDT|MDST|MDT|MEST|MET|MHT' \
                    '|MIST|MIT|MMT|MOST|MOT|MPT|MSD|MSK|MSM|MST|MUST|MUT|MVT|MWT|MYT|NCST|NCT|NDDT|NDT|NEGT|NEST|NET' \
                    '|NFT|NMT|NOVST|NOVT|NPT|NRT|NST|NT|NUT|NWT|NZDT|NZMT|NZST|OMSST|OMST|ORAST|ORAT|PDDT|PDT|PEST' \
                    '|PET|PETST|PETT|PGT|PHOT|PHST|PHT|PKST|PKT|PLMT|PMDT|PMMT|PMST|PMT|PNT|PONT|PPMT|PPT|PST|PT|PWT' \
                    '|PYST|PYT|QMT|QYZST|QYZT|RET|RMT|ROTT|SAKST|SAKT|SAMT|SAST|SBT|SCT|SDMT|SDT|SET|SGT|SHEST|SHET' \
                    '|SJMT|SLT|SMT|SRET|SRT|SST|STAT|SVEST|SVET|SWAT|SYOT|TAHT|TASST|TAST|TBIST|TBIT|TBMT|TFT|THA|TJT' \
                    '|TKT|TLT|TMT|TOST|TOT|TRST|TRT|TSAT|TVT|ULAST|ULAT|URAST|URAT|UTC|UYHST|UYST|UYT|UZST|UZT|VET' \
                    '|VLAST|VLAT|VOLST|VOLT|VOST|VUST|VUT|WARST|WART|WAST|WAT|WDT|WEDT|WEMT|WEST|WET|WFT|WGST|WGT|WIB' \
                    '|WIT|WITA|WMT|WSDT|WSST|WST|WT|XJT|YAKST|YAKT|YAPT|YDDT|YDT|YEKST|YEKST|YEKT|YEKT|YERST|YERT|YPT' \
                    '|YST|YWT|zzz '
# explicit north american timezones that get replaced
NA_TIMEZONES_PATTERN = 'pacific|eastern|mountain|central'
ALL_TIMEZONES_PATTERN = TIMEZONES_PATTERN + '|' + NA_TIMEZONES_PATTERN
DELIMITERS_PATTERN = '[/\:\-\,\s\_\+\@]+'

TIME_PERIOD_PATTERN = 'a\.m\.|am|p\.m\.|pm'
# can be in date strings but not recognized by dateutils
EXTRA_TOKENS_PATTERN = 'due|by|on|standard|daylight|savings|time|date|\sof\s|\sto\s|until|z|at|t'

# Allows for straightforward datestamps e.g 2017, 201712, 20171223. Created with:
# YYYYMM_PATTERN = '|'.join(['19\d\d'+'{:0>2}'.format(mon)+'|20\d\d'+'{:0>2}'.format(mon) for mon in range(1, 13)])
# YYYYMMDD_PATTERN = '|'.join(['19\d\d'+'{:0>2}'.format(mon)+'[0123]\d|20\d\d'+'{:0>2}'.format(mon)+'[0123]\d'
#   for mon in range(1, 13)])
YYYY_PATTERN = '19\d\d|20\d\d'
YYYYMM_PATTERN = '19\d\d01|20\d\d01|19\d\d02|20\d\d02|19\d\d03|20\d\d03|19\d\d04|20\d\d04|19\d\d05|20\d\d05|19\d\d06' \
                 '|20\d\d06|19\d\d07|20\d\d07|19\d\d08|20\d\d08|19\d\d09|20\d\d09|19\d\d10|20\d\d10|19\d\d11|20\d\d11' \
                 '|19\d\d12|20\d\d12 '
YYYYMMDD_PATTERN = "19\d\d01[0123]\d|20\d\d01[0123]\d|19\d\d02[0123]\d|20\d\d02[0123]\d|19\d\d03[0123]\d|20\d\d03[" \
                   "0123]\d|19\d\d04[0123]\d|20\d\d04[0123]\d|19\d\d05[0123]\d|20\d\d05[0123]\d|19\d\d06[" \
                   "0123]\d|20\d\d06[0123]\d|19\d\d07[0123]\d|20\d\d07[0123]\d|19\d\d08[0123]\d|20\d\d08[" \
                   "0123]\d|19\d\d09[0123]\d|20\d\d09[0123]\d|19\d\d10[0123]\d|20\d\d10[0123]\d|19\d\d11[" \
                   "0123]\d|20\d\d11[0123]\d|19\d\d12[0123]\d|20\d\d12[0123]\d "
# YYYYMMDDHHMMSS_PATTERN = ''
# '|'.join(['19\d\d' + '{:0>2}'.format(mon) + '[0-3]\d[0-5]\d[0-5]\d[0-5]\d|20\d\d' + '{:0>2}'.format(mon) +
#   '[0-3]\d[0-5]\d[0-5]\d[0-5]\d' for mon in range(1, 13)])
UNDELIMITED_STAMPS_PATTERN = '|'.join([YYYYMMDD_PATTERN, YYYYMM_PATTERN])

# TODO: Get english numbers?
# http://www.rexegg.com/regex-trick-numbers-in-english.html

RELATIVE_PATTERN = 'before|after|next|last|ago'
RELATIVE_PATTERN_NEG_POST = 'before|ago|back|since'
RELATIVE_PATTERN_POS_PRE = 'after|next'
RELATIVE_PATTERN_POS_POST = 'until'
TIME_SHORTHAND_PATTERN = 'noon|midnight|today|yesterday'

# Time pattern is used independently, so specified here.
TIME_PATTERN = """
(?P<time>
    ## Captures in format XX:YY(:ZZ) (PM) (EST)
    (
        (?P<hours>\d{{1,2}})
        \:
        (?P<minutes>\d{{1,2}})
        (\:(?<seconds>\d{{1,2}}))?
        ([\.\,](?<microseconds>\d{{1,6}}))?
        \s*
        (?P<time_periods>{time_periods})?
        \s*
        (?P<timezones>{timezones})?
    )
    |
    ## Captures in format 11 AM (EST)
    ## Note with single digit capture requires time period
    (
        (?P<hours>\d{{1,2}})
        \s*
        (?P<time_periods>{time_periods})
        \s*
        (?P<timezones>{timezones})*
    )
)
""".format(
    time_periods=TIME_PERIOD_PATTERN,
    timezones=ALL_TIMEZONES_PATTERN
)

DATES_PATTERN = """
(
    (
        {time}
        |
        ## Undelimited datestamps (treated prior to digits)
        (?P<undelimited_stamps>{undelimited_stamps})
        |
        ## Grab any four digit years
        (?P<years>{years})
        |
        ## Grab any digits
        (?P<digits_modifier>{digits_modifier})
        |
        (?P<digits>{digits})
        |
        (?P<days>{days})
        |
        (?P<months>{months})
        |
        ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
        ## as well as whitespace
        (?P<delimiters>{delimiters})
        |
        ## These tokens could be in phrases that dateutil does not yet recognize
        ## Some are US Centric
        (?P<extra_tokens>{extra_tokens})
    ## We need at least three items to match for minimal datetime parsing
    ## ie 10pm
    ){{3,}}
)
"""

DATES_PATTERN = DATES_PATTERN.format(
    time=TIME_PATTERN,
    undelimited_stamps=UNDELIMITED_STAMPS_PATTERN,
    years=YYYY_PATTERN,
    digits=DIGITS_PATTERN,
    digits_modifier=DIGITS_MODIFIER_PATTERN,
    days=DAYS_PATTERN,
    months=MONTHS_PATTERN,
    delimiters=DELIMITERS_PATTERN,
    extra_tokens=EXTRA_TOKENS_PATTERN
)

DATE_REGEX = re.compile(DATES_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

TIME_REGEX = re.compile(TIME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

# These tokens can be in original text but dateutil
# won't handle them without modification
REPLACEMENTS = {
    "standard": " ",
    "daylight": " ",
    "savings": " ",
    "time": " ",
    "date": " ",
    "by": " ",
    "due": " ",
    "on": " ",
    "to": " ",
}

TIMEZONE_REPLACEMENTS = {
    "pacific": "PST",
    "eastern": "EST",
    "mountain": "MST",
    "central": "CST",
}

# Characters that can be removed from ends of matched strings
STRIP_CHARS = ' \n\t:-.,_'

SECOND_PATTERN = 'sec|second|s'
AMBIG_PATTERN = 'm'
MINUTE_PATTERN = 'min|minute'
HOUR_PATTERN = 'h|hr|hour'
DAY_PATTERN = 'd|day'
WEEK_PATTERN = 'w|wk|week'
MONTH_PATTERN = 'mon|month'
YEAR_PATTERN = 'y|yr|year'

UNIT_PATTERN = '''
(?:
(?P<relative_pos_pre>{r3})?
(?P<number>\d{{1,2}})
\W*
(?P<fraction>\.\d{{1,2}}|\d{{1,2}}/\d{{1,2}})?
\W*
(?:
    (?P<year>{year_pattern}) | 
    (?P<month>{month_pattern}) | 
    (?P<ambig>{ambig_pattern}) |
    (?P<week>{week_pattern}) | 
    (?P<day>{day_pattern}) | 
    (?P<hour>{hour_pattern}) | 
    (?P<minute>{minute_pattern}) |
    (?P<second>{second_pattern}) 
)s?
\W*
)+
(?P<relative_pos_post>{r2})?
(?P<relative_neg_post>{r1})?
(?:\W|$)
'''.format(
    ambig_pattern=AMBIG_PATTERN,
    second_pattern=SECOND_PATTERN,
    minute_pattern=MINUTE_PATTERN,
    hour_pattern=HOUR_PATTERN,
    day_pattern=DAY_PATTERN,
    week_pattern=WEEK_PATTERN,
    month_pattern=MONTH_PATTERN,
    year_pattern=YEAR_PATTERN,
    r1=RELATIVE_PATTERN_NEG_POST,
    r2=RELATIVE_PATTERN_POS_POST,
    r3=RELATIVE_PATTERN_POS_PRE
)
UNIT_RX = re.compile(UNIT_PATTERN,
                     re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

EXTRACT_PATTERN = '''
(?:
(?P<number>\d{{1,2}})
\W*
(?P<fraction>\.\d{{1,2}}|\d{{1,2}}/\d{{1,2}})?
\W*
(?:
    (?P<year>{year_pattern}) | 
    (?P<month>{month_pattern}) | 
    (?P<ambig>{ambig_pattern}) |
    (?P<week>{week_pattern}) | 
    (?P<day>{day_pattern}) | 
    (?P<hour>{hour_pattern}) | 
    (?P<minute>{minute_pattern}) |
    (?P<second>{second_pattern}) 
)s?
\W*
)
(?=\d|\W|$)
'''.format(
    ambig_pattern=AMBIG_PATTERN,
    second_pattern=SECOND_PATTERN,
    minute_pattern=MINUTE_PATTERN,
    hour_pattern=HOUR_PATTERN,
    day_pattern=DAY_PATTERN,
    week_pattern=WEEK_PATTERN,
    month_pattern=MONTH_PATTERN,
    year_pattern=YEAR_PATTERN
)
EXTRACT_RX = re.compile(EXTRACT_PATTERN,
                        re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)
