#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re

entries = []
categories = {}
tags = {}

month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

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
                    
                    categories_here = []
                    categories_match = re.search(r'<p>Categories: (.+?)</p>', content)
                    if categories_match:
                        categories_here = categories_match.group(1).split(', ')
                        for category in categories_here:
                            if category in categories:
                                categories[category] += [index_link]
                            else:
                                categories[category] = [index_link]
                    else:
                        print(f"didn't find categories for {path}")
                    
                    tags_here = []
                    tags_match = re.search(r'<p>Tags: (.+?)</p>', content)
                    if tags_match:
                        tags_here = tags_match.group(1).split(', ')
                        for tag in tags_here:
                            if tag in tags:
                                tags[tag] += [index_link]
                            else:
                                tags[tag] = [index_link]
                    else:
                        print(f"didn't find tags for {path}")
                    
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
    with open(f"{file_name}.md", "w") as index_file_md, open(f"{file_name}.html", "w") as index_file_html, open(html_template_file_name, "r") as html_template_file:
        index_content_html = ""
        sorted_links = sorted(data.keys(), key=lambda x: x.lower())
        for link in sorted_links:
            search_result = re.search(r'>(.*)<', link)
            if not search_result:
                continue
            keyword = search_result.group(1)
            index_file_md.write(f"\n### {keyword}\n\n")
            index_content_html += f"<h3 id='{keyword}'>{keyword}</h3>\n\n<ul>\n"
            for item in data[link]:
                index_file_md.write(f"* {item[1]}\n")
                index_content_html += f"<li>{item[0]}</li>\n"
            index_content_html += f"</ul>\n\n"
        template_content = html_template_file.read()
        html_out = template_content.replace('<div class="content"></div>', f'<div class="content">{index_content_html}</div>')
        index_file_html.write(html_out)

# Writing unique categories and tags to files
create_collection(file_name = "categories", data = categories, html_template_file_name = "categories_template.html")

create_collection(file_name = "tags", data = tags, html_template_file_name = "tags_template.html")
