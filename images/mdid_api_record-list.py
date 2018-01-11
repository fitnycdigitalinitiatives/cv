#!/usr/bin/env python

import sys
import os
import pprint
import json
import cooperhewitt.roboteyes.colors.palette as palette
import cooperhewitt.swatchbook as sb
import urllib
import csv
from PIL import Image
import requests
from io import BytesIO



# open csv file
filename = 'barbier-metadata.csv'
b = open(filename, 'wb')
a = csv.writer(b)
f = open('barbier-list.csv', 'rb')
reader = csv.reader(f)
record_names = list(reader)



#create csv labels
data = [['title', 'record-name', 'record-id', 'color-data', 'facet-color', 'primary-color', 'width', 'height']]
missing = []



for row in record_names:

	record_name = str(row[0])
	print record_name
	with requests.session() as s:

		try:
			url = 'https://fitdil.fitnyc.edu/api/search/?kw=' + record_name + '/'
			api = urllib.urlopen(url).read()
			json_data = json.loads(api)
			record = json_data['records']
			record = record[0]
			title = record['title']
			record_id = record['id']
			#run color analysis
			image_url = 'https://fitdil.fitnyc.edu/media/get/' + str(record_id) + '/' + record_name + '/900x600/'
			local_filename, headers = urllib.urlretrieve(image_url)
			path = local_filename

			# Where ref is a valid cooperhewitt.swatchbook color palette
			ref = 'css4'
			color_data = palette.extract_roygbiv(path, ref)
			cdp = color_data['palette']
			facet_color_l = []
			for swatch in cdp:
				closest = swatch["closest"]
				closest_s = str(closest)
				facet_color_l.append(closest_s)
			facet_color = "|".join(facet_color_l)
			primary_1 = cdp[0]
			primarycolor_1 = primary_1['color']
			color_1, name_1 = sb.closest('basic', primarycolor_1)
			if len(cdp) > 1 :
				primary_2 = cdp[1]
				primarycolor_2 = primary_2['color']
				color_2, name_2 = sb.closest('basic', primarycolor_2)
				primary_color = color_1 + '|' + color_2
			else:
				primary_color = compile

			#get image dimensions
			full_image_url = 'https://fitdil.fitnyc.edu/media/get/' + str(record_id) + '/' + record_name + '/'
			req = s.get(full_image_url, headers={'User-Agent':'Mozilla5.0(Google spider)','Range':'bytes=0-{}'.format(5000)})
			im = Image.open(BytesIO(req.content))
			width, height = im.size
			print str(width) + 'x' + str(height)
			im.close()


			#append value to labels
			data.append([str(title.encode("UTF-8") if title else title), record_name, record_id, json.dumps(color_data), facet_color, primary_color, width, height])

		except: # catch *all* exceptions
		  e = sys.exc_info()[0]
		  print e
		  missing.append(record_name)



print 'Missing='
print missing




print 'completed: ' + filename
a.writerows(data)
b.close()
f.close()
