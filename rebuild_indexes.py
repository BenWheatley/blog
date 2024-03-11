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
with open('sorted_index.txt', 'w') as output_file:
    current_year = ""
    current_month = ""
    for entry in sorted_entries:
        year, month, date = entry['date'].split("/")
        if year != current_year:
            current_year = year
            output_file.write(f"\n## {current_year}\n")
        if month != current_month:
            current_month = month
            output_file.write(f"\n### {month_names[int(current_month)-1]}\n\n")
        link = entry['link']
        output_file.write(f"* [{date} - {entry['title']}]({link})\n")

# Writing unique categories and tags to files
with open('categories.txt', 'w') as categories_file:
    categories_file.write('\n'.join(sorted(categories)))

with open('tags.txt', 'w') as tags_file:
    tags_file.write('\n'.join(sorted(tags)))

def create_view_list(from_keyword, model_type_name, model_list):
    with open(f'{model_type_name}/{from_keyword}', 'w') as list_file:
        list_file.write("example data") # All blog posts that match