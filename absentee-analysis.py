#!/usr/bin/env python
# coding: utf-8

#
# streets.txt --- hand-coded
# ORANGE_absentee_20201103.csv --- from https://www.ncsbe.gov/results-data/absentee-data (https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2020_11_03/absentee_county_20201103.zip)
#



import codecs
import csv
import re
import time



time_start = time.time()



streets = {}
with open( './streets.txt' ) as csv_file:
    csv_reader = csv.DictReader( filter( lambda x: x[0] != '#', csv_file ) )
    for row in csv_reader:
        streets[row['street']] = {
            'name': row['street'],
            're':   re.compile( '%s' % row['street'].upper() ),
            'min':  int( row['min'] ) if row['min'] else 0,
            'max':  int( row['max'] ) if row['max'] else 1e6
        }
        
        
        
voters     = []
address_re = re.compile( '^\\s*(\\d+)')
with open( './ncvoter68.txt' ) as csv_file:
    csv_reader = csv.DictReader( csv_file, delimiter = '\t' )
    for row in csv_reader:
        if row['voter_status_desc'] != 'ACTIVE':
            continue
        
        for street in streets:
            if streets[street]['re'].search( row['res_street_address'] ):
                re_res = address_re.match( row['res_street_address'] )
                if not re_res:
                    break
                    
                address = int( re_res.group( 1 ) )
                if address >= streets[street]['min'] and address <= streets[street]['max']:
                    voters.append( row )
                    
                break
        

                
voteds   = []
statuses = {}
with codecs.open( './ORANGE_absentee_20201103.csv', encoding = 'utf8', errors = 'ignore' ) as csv_file:
    csv_reader = csv.DictReader( csv_file, delimiter = "," )
    for row in csv_reader:
        statuses[row['ballot_rtn_status']] = True
        for street in streets:
            if streets[street]['re'].search( row['voter_street_address'] ):
                re_res = address_re.match( row['voter_street_address'] )
                if not re_res:
                    break
                    
                address = int( re_res.group( 1 ) )
                if address >= streets[street]['min'] and address <= streets[street]['max']:
                    voteds.append( row )
                    
                break
                
                
                
time_end = time.time()
print( 'Data processed in %0.2fs.\n' % ( time_end - time_start ) )

print( '\nList of ballot statuses:' )
for status in statuses:
    print( '  %s' % status )
                

                




#
# Summarize
#
print( 'Found %d voted out of %d voters.\n' % ( len( voteds ), len( voters ) ) )

street_stats = { street.upper(): { 'registered': 0, 'total': 0 } for street in streets }
for street in street_stats.keys():
    for status in statuses:
        street_stats[street][status] = 0
        
        
for row in voters:
    for street in streets:
        if streets[street]['re'].search( row['res_street_address'] ):
            street_stats[street.upper()]['registered'] += 1
            break
        
        
for row in voteds:
    for street in streets:
        if streets[street]['re'].search( row['voter_street_address'] ):
            street_stats[street.upper()][row['ballot_rtn_status']] += 1
            street_stats[street.upper()]['total'] += 1
            break




street_summary = {
    street: {
        'name':       street,
        'registered': int( street_stats[street]['registered'] ),
        'voted':      int( street_stats[street]['ACCEPTED'] + street_stats[street]['ACCEPTED - CURED'] ),
        'spoiled':    int( street_stats[street]['SPOILED'] + street_stats[street]['WITNESS INFO INCOMPLETE'] )
    }
    for street in street_stats.keys()
}

total_registered = sum( [ street_summary[street]['registered'] for street in street_summary ] )
total_voted      = sum( [ street_summary[street]['voted'] for street in street_summary ] )

print( 'OVERALL TURNOUT IS %0.2f%% (%d of %d)\n\n' % ( total_voted / total_registered * 100, total_voted, total_registered ) )

spoiled_count = sum( [ street_summary[street]['spoiled'] for street in street_summary ] )
if spoiled_count > 0:
    print( '----------\nSPOILED BALLOTS:' )
    for street in street_summary:
        street = street_summary[street]
        if street['spoiled'] > 0:
            print( '  %s: %d ballot%s' % ( street['name'], street['spoiled'], 's' if street['spoiled'] > 1 else '' ) )

else:
    print( '----------\nNO SPOILED BALLOTS!' )
        
print( '----------\n\n' )

print( 'TURNOUT BY STREET:' )
for street in sorted( street_summary.keys() ):
    street = street_summary[street]
    if street['registered'] > 0:
        print( '  {:<16s} {:=3.2f}% ({:>3d} of {:>3d})'.format( street['name'] + ':', street['voted'] / street['registered'] * 100, street['voted'], street['registered'] ) )
    else:
        print( '  {:<16s} --- NO REGISTERED VOTERS ---'.format( street['name'] + ':' ) )
        
        
        
print( '\n\nTURNOUT BY ADDRESS:' )
turnout_dict = {
    street: street_summary[street.upper()]['voted'] / ( street_summary[street.upper()]['registered'] if street_summary[street.upper()]['registered'] > 0 else 1 )
    for street in streets
}

rank = 1
for street in sorted( zip( turnout_dict.keys(), [ turnout_dict[street] for street in turnout_dict.keys() ] ), key = lambda x: -x[1] ):
    print( '  #{:=2d} {:<16} {:=3.2f}% ({:=3d} of {:=3d})'.format( rank, street[0] + ':', street[1] * 100, street_summary[street[0].upper()]['voted'], street_summary[street[0].upper()]['registered'] ) )
    rank += 1




for street in street_stats:
    print( '  {:>16} {}'.format( street + ':', street_stats[street]['ACCEPTED - CURED'] ) )






