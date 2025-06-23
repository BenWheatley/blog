#!/usr/bin/python3
# -*- coding: utf-8 -*-

def main():
	import os
	import re
	import html
	import logging
	
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)
	
	entries = []
	categories = {}
	tags = {}
	
	month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	
	def extract_metadata(content, label, index_link, storage_dict, path):
		match = re.search(rf"<p>{label}:(.*?)</p>", content, re.DOTALL | re.IGNORECASE)
		if not match:
			logger.warning(f"didn't find {label.lower()} in content for {path}")
			return []
		
		links = re.findall(r"<a [^>]*?href=['\"](?:.*?)#(.*?)['\"][^>]*?>(.*?)</a>", match.group(1), re.DOTALL)
		results = []
		
		for _, visible_text in links:
			raw_key = html.unescape(visible_text.strip())
			
			# Normalization key: lowercase + strip + replace common dividers
			normalized_key = re.sub(r'[\s_-]+', ' ', raw_key.strip().lower())
			
			# Store raw version to preserve original capitalisation
			canonical_display = (
				raw_key if re.match(r'^[A-Z0-9 ]+$', raw_key.strip())  # likely an initialism
				else raw_key.strip().capitalize()
			)
			
			if normalized_key not in storage_dict:
				storage_dict[normalized_key] = (set(), [])  # set of visible variants, list of index links
			
			storage_dict[normalized_key][0].add(raw_key.strip())
			storage_dict[normalized_key][1].append(index_link)
			
			results.append(raw_key.strip())  # return the original tag as used
		
		return results
	
	for root, dirs, files in os.walk('./'):
		for file in files:
			if file.endswith('.html'):
				path = os.path.join(root, file)
				with open(path, 'r') as f:
					content = f.read()
					date_match = re.search(r'(\d{4}/\d{2}/\d{2})', path)
					title_match = re.search(r'<h1>(.+?)</h1>', content)
					
					if date_match and title_match:
						date = date_match.group(1)
						title = title_match.group(1)
						year, month, _ = date.split("/")
						filename = file
						link = f"{year}/{month}/{filename}"
						
						html_link = f"<a href='{link}'>{title} ({date})</a>"
						md_link = f"[{title} ({date})]({link})"
						index_link = (html_link, md_link)
						
						categories_here = extract_metadata(content, "Categories", index_link, categories, path)
						tags_here = extract_metadata(content, "Tags", index_link, tags, path)
						
						entries.append({'link': link, 'date': date, 'title': title, 'categories': categories_here, 'tags': tags_here})
	
	# Sorting entries chronologically
	sorted_entries = sorted(entries, key=lambda x: x['date'], reverse=True)
	
	# Writing the sorted index to a file
	with open('index.md', 'w') as output_file_md, open("index.html", "w") as output_file_html, open("home_template.html", "r") as template_file:
		current_year = ""
		current_month = ""
		output_html = ""
		outside_of_a_list = True
		fresh_start = True
		for entry in sorted_entries:
			year, month, date = entry['date'].split("/")
			if not fresh_start and (year != current_year or month != current_month):
				output_html += "</ul>\n"
			fresh_start = False
			if year != current_year:
				current_year = year
				output_file_md.write(f"\n## {current_year}\n")
				output_html += (f"\n<h2>{current_year}</h2>\n")
				outside_of_a_list = True
			if month != current_month:
				current_month = month
				month_string = month_names[int(current_month)-1]
				output_file_md.write(f"\n### {month_string}\n\n")
				output_html += (f"\n<h3>{month_string}</h3>\n\n")
				outside_of_a_list = True
			if outside_of_a_list:
				outside_of_a_list = False
				output_html += "<ul>\n"
			link = entry['link']
			title = entry['title']
			output_file_md.write(f"* [{date} - {title}]({link})\n")
			output_html += (f"<li><a href='{link}'>{date} - {title}</a></li>\n")
		output_html += "</ul>\n"
		template_content = template_file.read()
		html_out = template_content.replace('<div class="content"></div>', f'<div class="content">{output_html}</div>')
		output_file_html.write(html_out)
	
	def create_collection(file_name, data, html_template_file_name):
		with open(f"{file_name}.md", "w") as index_file_md, \
			 open(f"{file_name}.html", "w") as index_file_html, \
			 open(html_template_file_name, "r") as html_template_file:
			
			index_content_html = ""
			
			for normalized_key in sorted(data.keys()):
				variants, entries = data[normalized_key]
				# Pick a display label: use the first variant that looks like an initialism if present, else sentence-case
				def choose_display_label(vs):
					for v in vs:
						if re.match(r'^[A-Z0-9 ]+$', v):  # all caps → initialism
							return v
					return sorted(vs)[0].capitalize()
				
				display_label = choose_display_label(variants)
				
				# Add HTML anchors — reserve normalized_key for header
				alternate_anchors = sorted(set(variants) - {normalized_key})
				for anchor_id in alternate_anchors:
					index_content_html += f"<a id='{anchor_id}'></a>\n"
				
				index_file_md.write(f"\n### {display_label}\n\n")
				index_content_html += f"<h3 id='{normalized_key}'>{display_label}</h3>\n<ul>\n"
			
				for item in entries:
					index_file_md.write(f"* {item[1]}\n")
					index_content_html += f"<li>{item[0]}</li>\n"
				index_content_html += f"</ul>\n\n"
			
			template_content = html_template_file.read()
			html_out = template_content.replace(
				'<div class="content"></div>',
				f'<div class="content">{index_content_html}</div>'
			)
			index_file_html.write(html_out)
	
	# Writing unique categories and tags to files
	create_collection(file_name = "categories", data = categories, html_template_file_name = "categories_template.html")
	
	create_collection(file_name = "tags", data = tags, html_template_file_name = "tags_template.html")

if __name__ == "__main__":
	main()
