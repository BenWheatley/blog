#!/usr/bin/python3
# -*- coding: utf-8 -*-

def main():
	import os
	import re
	import xml.etree.ElementTree as ET
	from datetime import datetime
	import hashlib
	import html
	from urllib.parse import quote

	# RSS feed metadata
	FEED_TITLE = "Blog - Kitsune Software"
	FEED_LINK = "https://benwheatley.github.io/blog/"
	FEED_DESCRIPTION = "A blog about technology, AI, and various other topics"
	FEED_LANGUAGE = "en-gb"

	def clean_title(title_text):
		"""Remove HTML entities and tags from title"""
		# Decode HTML entities
		cleaned = html.unescape(title_text)
		# Remove any HTML tags
		cleaned = re.sub(r'<[^>]+>', '', cleaned)
		return cleaned

	def fix_relative_urls(content_html, base_path):
		"""Convert relative URLs to absolute URLs"""
		# Fix relative image sources
		content_html = re.sub(
			r'src=["\'](?!http)([^"\']+)["\']',
			lambda m: f'src="{base_path}{quote(m.group(1))}"',
			content_html
		)
		# Fix relative hrefs
		content_html = re.sub(
			r'href=["\'](?!http|#|mailto:)([^"\']+)["\']',
			lambda m: f'href="{base_path}{quote(m.group(1))}"',
			content_html
		)
		return content_html

	entries = []

	# Scan all HTML files and extract metadata
	for root, dirs, files in os.walk('./'):
		for file in files:
			if file.endswith('.html'):
				path = os.path.join(root, file)

				# Skip template and index files
				if 'template.html' in path or path.startswith('./index.html') or path.startswith('./tags.html') or path.startswith('./categories.html'):
					continue

				with open(path, 'r') as f:
					content = f.read()

					# Extract date from path (format: ./year/month/filename.html)
					date_match = re.search(r'(\d{4})/(\d{2})/([^/]+\.html)', path)
					if not date_match:
						continue

					year = date_match.group(1)
					month = date_match.group(2)
					filename = date_match.group(3)

					# Extract title from h1 tag
					title_match = re.search(r'<h1>(.+?)</h1>', content)
					if not title_match:
						continue

					title = title_match.group(1)

					# Parse filename to get day and time if available (format: DD-HH.MM.SS.html)
					day_time_match = re.search(r'(\d{2})-(\d{2})\.(\d{2})\.(\d{2})\.html', filename)
					if day_time_match:
						day = day_time_match.group(1)
						hour = day_time_match.group(2)
						minute = day_time_match.group(3)
						second = day_time_match.group(4)
					else:
						# Try just day (DD.html)
						day_match = re.search(r'(\d{2})\.html', filename)
						if day_match:
							day = day_match.group(1)
							hour, minute, second = "12", "00", "00"
						else:
							continue

					# Create datetime object
					try:
						pub_date = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
					except ValueError:
						continue

					# Extract content from <div class="content">
					content_match = re.search(r'<div class="content">(.+?)</div>\s*<hr />', content, re.DOTALL)
					if content_match:
						post_content = content_match.group(1)
					else:
						post_content = title

					# Build absolute link and base path for this post
					link = f"{FEED_LINK}{year}/{month}/{filename}"
					base_path = f"{FEED_LINK}{year}/{month}/"

					# Clean title and fix URLs in content
					clean_title_text = clean_title(title)
					fixed_content = fix_relative_urls(post_content, base_path)

					# Store entry
					entries.append({
						'title': clean_title_text,
						'link': link,
						'description': fixed_content,
						'pub_date': pub_date,
						'guid': link
					})

	# Sort entries by date (most recent first)
	entries.sort(key=lambda x: x['pub_date'], reverse=True)

	# Limit to most recent 20 entries (standard RSS practice)
	entries = entries[:20]

	# Build RSS feed with atom namespace
	rss = ET.Element('rss', version='2.0')
	rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
	channel = ET.SubElement(rss, 'channel')

	# Channel metadata
	ET.SubElement(channel, 'title').text = FEED_TITLE
	ET.SubElement(channel, 'link').text = FEED_LINK
	ET.SubElement(channel, 'description').text = FEED_DESCRIPTION
	ET.SubElement(channel, 'language').text = FEED_LANGUAGE

	# Add atom:link for self-reference (required for validation)
	atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
	atom_link.set('href', f'{FEED_LINK}rss.xml')
	atom_link.set('rel', 'self')
	atom_link.set('type', 'application/rss+xml')

	if entries:
		# lastBuildDate is the most recent post date
		last_build = entries[0]['pub_date'].strftime('%a, %d %b %Y %H:%M:%S +0000')
		ET.SubElement(channel, 'lastBuildDate').text = last_build

	# Add items
	for entry in entries:
		item = ET.SubElement(channel, 'item')
		ET.SubElement(item, 'title').text = entry['title']
		ET.SubElement(item, 'link').text = entry['link']
		ET.SubElement(item, 'description').text = entry['description']
		ET.SubElement(item, 'pubDate').text = entry['pub_date'].strftime('%a, %d %b %Y %H:%M:%S +0000')
		ET.SubElement(item, 'guid', isPermaLink='true').text = entry['guid']

	# Generate XML string
	tree = ET.ElementTree(rss)
	ET.indent(tree, space='  ')

	# Convert to string
	import io
	output = io.BytesIO()
	tree.write(output, encoding='utf-8', xml_declaration=True)
	xml_content = output.getvalue().decode('utf-8')

	# Add CSS stylesheet reference after XML declaration
	xml_lines = xml_content.split('\n', 1)
	if len(xml_lines) == 2:
		new_content = xml_lines[0] + '\n<?xml-stylesheet type="text/css" href="rss.css"?>\n' + xml_lines[1]
	else:
		new_content = xml_content

	# Calculate hash of new content
	new_hash = hashlib.sha256(new_content.encode('utf-8')).hexdigest()

	rss_file = 'rss.xml'

	# Check if file exists and compare hashes (idempotent operation)
	should_write = True
	if os.path.exists(rss_file):
		with open(rss_file, 'r') as f:
			old_content = f.read()
			old_hash = hashlib.sha256(old_content.encode('utf-8')).hexdigest()
			if old_hash == new_hash:
				should_write = False
				print(f"RSS feed is up to date (hash: {new_hash[:16]}...)")

	# Write file only if changed
	if should_write:
		with open(rss_file, 'w') as f:
			f.write(new_content)
		print(f"RSS feed written to {rss_file} ({len(entries)} entries, hash: {new_hash[:16]}...)")

	return len(entries)

if __name__ == "__main__":
	main()
