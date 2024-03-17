import os
import re

entries = []
categories = set()
tags = set()

month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

for root, dirs, files in os.walk('./'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
                date_match = re.search(r'(\d{4}/\d{2}/\d{2})', path)
                title_match = re.search(r'<h1>(.+?)</h1>', content)
                
                categories_here = []
                categories_match = re.search(r'<p>Categories: (.+?)</p>', content)
                if categories_match:
                    categories_here = categories_match.group(1).split(', ')
                    categories.update(categories_here)
                else:
                    print(f"didn't find categories for {path}")
                
                tags_here = []
                tags_match = re.search(r'<p>Tags: (.+?)</p>', content)
                if tags_match:
                    tags_here = tags_match.group(1).split(', ')
                    tags.update(tags_here)
                else:
                    print(f"didn't find tags for {path}")
                
                if date_match and title_match:
                    date = date_match.group(1)
                    title = title_match.group(1)
                    year, month, _ = date.split("/")
                    filename = file
                    link = f"{year}/{month}/{filename}"
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

# Writing unique categories and tags to files
with open('categories.txt', 'w') as categories_file:
    categories_file.write('\n'.join(sorted(categories)))

with open('tags.txt', 'w') as tags_file:
    tags_file.write('\n'.join(sorted(tags)))

def create_view_list(from_keyword, model_type_name, model_list):
    with open(f'{model_type_name}/{from_keyword}', 'w') as list_file:
        list_file.write("example data") # All blog posts that match